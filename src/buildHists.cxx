#include "buildHists.hh"
#include "TreeBuffer.hh"
#include "Jet.hh"
#include "JetPerfHists.hh"
#include "misc_func.hh"
#include "jtag.hh"

#include "H5Cpp.h"

#include <vector>
#include <string>
#include <cmath>
#include <stdexcept>

int buildHists(std::vector<std::string> files, std::string out_name,
	       unsigned flags){
  const bool test = (flags & jtag::test);
  if (exists(out_name)) throw std::runtime_error(out_name + " exists");

  TreeBuffer buffer(files);
  JetPerfHists hists;

  int test_events = std::min(int(100), buffer.size());
  const int n_events = test ? test_events: buffer.size();
  int total_jets = 0;
  if (test) printf("starting loop on %i events\n", n_events);
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
  if (test) buffer.saveSetBranches("required_branches.txt");
  if (test) printf("done event loop, saving\n");
  H5::H5File out_file(out_name.c_str(), H5F_ACC_EXCL);
  hists.writeTo(out_file);

  return 0;
}

