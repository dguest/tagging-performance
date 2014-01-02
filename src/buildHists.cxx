#include "buildHists.hh"
#include "TreeBuffer.h"
#include "Jet.hh"
#include "JetPerfHists.hh"
#include "misc_func.hh"

#include "H5Cpp.h"

#include <vector>
#include <string> 
#include <cmath> 
#include <stdexcept> 

int buildHists(std::vector<std::string> files, std::string out_name){ 
  if (exists(out_name)) throw std::runtime_error(out_name + " exists"); 

  TreeBuffer buffer(files); 

  JetPerfHists hists; 

  const int n_events = std::min(int(std::pow(10,6)), buffer.size()); 
  int total_jets = 0; 
  int error_jets = 0; 
  for (int event = 0; event < n_events; event++) { 
    buffer.getEntry(event); 
    const int n_jets = buffer.jet_pt->size(); 
    total_jets += n_jets; 
    for (int jidx = 0; jidx < n_jets; jidx++) { 
      Jet jet(buffer, jidx); 
      if (jet.pt < 20e3 || std::abs(jet.eta) > 2.5) continue; 
      hists.fill(jet, 1.0); 
    }
  }
  
  H5::H5File out_file(out_name, H5F_ACC_EXCL); 
  hists.writeTo(out_file); 
  if (error_jets) { 
    printf("%i of %i jets have errors (%f%%)\n", 
	   error_jets, total_jets, error_jets * 100.0 / total_jets); 
  }

  return 0; 
}

