#ifndef BUILD_HISTS_HH
#define BUILD_HISTS_HH

#include <vector> 
#include <string> 

namespace jtag { 
  const unsigned test = 1 << 0; 
}

int buildHists(std::vector<std::string> files, std::string out, 
	       unsigned flags = 0); 

#endif 
