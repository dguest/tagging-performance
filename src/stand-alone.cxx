#include "buildHists.hh"

#include <vector> 
#include <string> 
#include <cstring>

void usage(std::string call) { 
  printf("usage: %s [-h | -o <out file>] <root file>...\n", call.c_str()); 
}

int main(int narg, char* argv[]) { 
  std::string out_name = "test.h5"; 
  if (narg == 1) {
  }
  std::vector<std::string> files; 
  for (int pos = 1; pos < narg; pos++) { 
    if (argv[pos][0] == '-') { 
      if (strchr(argv[pos],'h')) { 
	usage(argv[0]); 
	exit(1); 
      }
      if (strchr(argv[pos], 'o')) { 
	if (pos + 1 < narg) { 
	  pos++; 
	  out_name = argv[pos]; 
	} else { 
	  printf("error: -o must be followed by an output file name\n"); 
	  exit(-1); 
	}
      }
    } else { 
      files.push_back(argv[pos]); 
    }
  }

  if (files.size() == 0) { 
    usage(argv[0]); 
    printf("error: no files\n"); 
    exit(-1);
  }

  return buildHists(files, out_name); 
}

