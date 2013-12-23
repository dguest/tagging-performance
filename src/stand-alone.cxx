#include "TreeBuffer.h"
#include "JetIter.hh"

#include <vector>
#include <string> 

int main(int narg, char* argv[]) { 
  std::vector<std::string> files = {"test.root"}; 
  TreeBuffer buffer(files); 
  const int n_events = std::min(1, buffer.size()); 
  for (int event = 0; event < n_events; event++) { 
    buffer.getEntry(event); 
    const int n_jets = buffer.jet_pt->size(); 
    for (int jidx = 0; jidx < n_jets; jidx++) { 
      printf("pt: %f\n", buffer.jet_pt->at(jidx)); 
    }
  }
  for (Jet jet: JetIter(buffer)) { 
    printf("iter pt: %f\n", jet.pt); 
  }

  return 0; 
}
