#include "MemoryMonitor.h"

using namespace std;
using namespace chrono;

int ReadSmaps(pid_t mother_pid, unsigned long values[5], bool& hasChildren,
	      bool verbose){

  hasChildren = false;
  
  std::vector<pid_t> cpids;
  char smaps_buffer[32];
  snprintf(smaps_buffer,32,"pstree -A -p %ld | tr \\- \\\\n",(long)mother_pid);
  FILE* pipe = popen(smaps_buffer, "r");
  if (pipe==0) {
    if (verbose)
      std::cerr << "MemoryMonitor: unable to open pstree pipe!" << std::endl;
    return 1;
  }
  
  char buffer[256];
  std::string result = "";
  while(!feof(pipe)) {
    if(fgets(buffer, 256, pipe) != NULL) {
      result += buffer;
      int pos(0);
      while(pos<256 && buffer[pos] != '\n' && buffer[pos] != '(') {
	pos++;}
      if(pos<256 && buffer[pos] == '(' && pos>1 && buffer[pos-1] != '}') {
	pos++;
	pid_t pt(0);
	while(pos<256 && buffer[pos] != '\n' && buffer[pos] != ')') {
	  pt=10*pt+buffer[pos]-'0';
	  pos++;}
	cpids.push_back(pt);} } } 
  pclose(pipe);
  
  if (cpids.size() > 1) hasChildren = true;
  
  long tsize(0);
  long trss(0);
  long tpss(0);
  long tswap(0);
  long tprd(0);
  std::vector<std::string> openFails;
  
  for(std::vector<pid_t>::const_iterator it=cpids.begin(); it!=cpids.end(); ++it) {
    snprintf(smaps_buffer,32,"/proc/%ld/smaps",(long)*it);

    FILE *file = fopen(smaps_buffer,"r");
    if(file==0) {
      openFails.push_back(std::string(smaps_buffer));} 
    else { 
      while(fgets(buffer,256,file)) {
	if(sscanf(buffer,"Size: %ld kB",&tsize)==1) values[0]+=tsize;
	if(sscanf(buffer,"Pss: %ld kB", &tpss)==1)  values[1]+=tpss;
	if(sscanf(buffer,"Rss: %ld kB", &trss)==1)  values[2]+=trss;
	if(sscanf(buffer,"Swap: %ld kB",&tswap)==1) values[3]+=tswap; 
	if(sscanf(buffer,"Private_Dirty: %ld kB",&tprd)==1) values[4]+=tprd; 
      } 
      fclose(file);} } 
  if(openFails.size()>3 && verbose) {
    std::cerr << "MemoryMonitor: too many failures in opening smaps files!" 
	      << std::endl;
    return 1; }
  return 0;
}

std::condition_variable cv;
std::mutex cv_m;
bool sigusr1 = false;

void SignalCallbackHandler(int /*signal*/) { std::unique_lock<std::mutex> l(cv_m); sigusr1 = true; cv.notify_one(); }

int MemoryMonitor(pid_t mpid, char* filename, std::chrono::milliseconds interval){
     
     signal(SIGUSR1, SignalCallbackHandler);

     Clock::time_point lastIteration = Clock::now() - interval;
     Clock::time_point currentTime;

     unsigned long values[5] = {0,0,0,0,0};
     int iteration = 1;
     int base = 0;
     int mem;
     bool mp(false);
     
     struct stat st;
     std::stringstream ss;
     ss << "/proc/" << mpid;
     if (stat(ss.str().c_str(), &st) != 0) return -1;
     int timestamp = st.st_mtime;
     int lastTimestamp = timestamp;

     std::ofstream file;
     file.open(filename);
     //     file << "time,pss,prd" << std::endl;

     
     // Monitoring loop until process exits
     while(kill(mpid, 0) == 0 && sigusr1 == false && lastTimestamp == timestamp){
        if (stat(ss.str().c_str(), &st) < 0)
          break;
        lastTimestamp = st.st_mtime;
	if (Clock::now() - lastIteration > interval) {
          
          iteration = iteration + 1;
          ReadSmaps( mpid, values, mp);
	  currentTime = Clock::now();


	  if (!mp) {
	    base = values[1] - values[4];
	    mem = values[4];
	  } else {
	    mem = values[1] - base;
	  }

	  file << duration_cast<nanoseconds>(currentTime.time_since_epoch()).count() << ",";
	  file << values[1] << "," << values[4] << "," << mem << std::endl;

          // Compute statistics
          for(int i=0;i<5;i++){
             values[i] = 0;
	  }
	  lastIteration = Clock::now();
	}
        
        std::unique_lock<std::mutex> lock(cv_m); 
        cv.wait_for(lock, milliseconds(200));     
     }
    file.close();

    return 0;
 }

int main(int argc, char *argv[]){

    if(argc != 7) { 
        std::cerr << "Usage: " << argv[0] << " --pid --filename --interval \n " <<  std::endl;
        return -1;}

    pid_t pid=-1; char* filename = NULL;
    std::chrono::milliseconds interval(1000);

    for (int i = 1; i < argc; ++i) {
      if (strcmp(argv[i], "--pid") == 0) pid = atoi(argv[i+1]); 
      else if (strcmp(argv[i],"--filename") == 0) filename = argv[i+1];
      //      else if (strcmp(argv[i], "--interval") == 0) interval = atoi(argv[i+1]);}
      else if (strcmp(argv[i], "--interval") == 0) interval = milliseconds(atoi(argv[i+1]));}

    if (pid < 2) {
      std::cerr << "Bad PID.\n";
      return 1;
    }
    MemoryMonitor(pid, filename, interval);

    return 0;
}


