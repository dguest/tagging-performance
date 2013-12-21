#include "TreeBuffer.hh"

#include <vector>
#include <string> 

int main(int narg, char* argv[]) { 
  std::vector<std::string> files = {"test.root"}; 
  TreeBuffer buffer(files); 
  return 0; 
}
