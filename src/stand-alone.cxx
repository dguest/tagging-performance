#include "buildHists.hh"

#include <vector> 
#include <string> 
#include <cstring>

void usage(std::string call) { 
  printf("usage: %s [-h] [-t] [-o <out file>] <root file>...\n", 
	 call.c_str()); 
}
void help() { 
  const char* help = 
    "\n"
    "Builds histograms and saves them in <out file>.\n"
    "Inputs are D3PDs, output is stored as HDF5.\n"
    "\n"
    "options: \n"
    " -h for help\n"
    " -t for test mode\n"
    " -o to set output file (defaults to test.h5)\n"
    "\n"
    "When in 'test mode', will print more diagnostics, run over fewer events\n"
    "and save all the used branches in required_branches.txt\n"; 
  puts(help); 
}

int main(int narg, char* argv[]) { 
  std::string out_name = "test.h5"; 
  if (narg == 1) {
    usage(argv[0]); 
    exit(1); 
  }
  std::vector<std::string> files; 
  unsigned flags = 0; 
  for (int pos = 1; pos < narg; pos++) { 
    if (argv[pos][0] == '-') { 
      if (strchr(argv[pos],'t')) flags |= jtag::test; 
      if (strchr(argv[pos],'h')) { 
	usage(argv[0]); 
	help(); 
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

  return buildHists(files, out_name, flags); 
}

