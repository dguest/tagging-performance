#include "TreeBuffer.h"
#include "Jet.hh"
#include "JetPerfHists.hh"
#include "misc_func.hh"

#include "H5Cpp.h"

#include <vector>
#include <string> 
#include <cmath> 
#include <stdexcept> 

int buildHists(std::vector<std::string> files, std::string out_name); 

int main(int narg, char* argv[]) { 
  std::string out_name = "test.h5"; 
  if (narg == 1) {
    printf("no files\n"); 
    exit(1);
  }
  std::vector<std::string> files; 
  for (int pos = 1; pos < narg; pos++) { 
    files.push_back(argv[pos]); 
  }
  return buildHists(files, out_name); 
}

int buildHists(std::vector<std::string> files, std::string out_name){ 
  if (exists(out_name)) throw std::runtime_error(out_name + " exists"); 

  TreeBuffer buffer(files); 

  JetPerfHists hists; 

  const int n_events = std::min(int(std::pow(10,6)), buffer.size()); 
  for (int event = 0; event < n_events; event++) { 
    buffer.getEntry(event); 
    const int n_jets = buffer.jet_pt->size(); 
    for (int jidx = 0; jidx < n_jets; jidx++) { 
      Jet jet(buffer, jidx); 
      if (jet.pt < 20e3 || std::abs(jet.eta) > 2.5) continue; 
      hists.fill(jet, 1.0); 
    }
  }
  
  H5::H5File out_file(out_name, H5F_ACC_EXCL); 
  hists.writeTo(out_file); 

  return 0; 
}
