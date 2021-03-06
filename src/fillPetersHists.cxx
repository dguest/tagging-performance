#include "buildHists.hh"
#include "PetersBuffer.hh"
#include "Jet.hh"
#include "PeterPerfHists.hh"
#include "misc_func.hh"
#include "jtag.hh"

#include "H5Cpp.h"

#include <vector>
#include <string>
#include <cmath>
#include <stdexcept>

int fillPetersHists(std::vector<std::string> files, std::string out_name,
	       unsigned flags){
  const bool test = (flags & jtag::test);
  if (exists(out_name)) throw std::runtime_error(out_name + " exists");

  PetersBuffer buffer(files);
  peter::FlavoredHists hists(flags);

  int test_events = std::min(int(100), buffer.size());
  const int n_events = test ? test_events: buffer.size();
  int total_jets = 0;
  if (test) printf("starting loop on %i events\n", n_events);
  for (int event = 0; event < n_events; event++) {
    buffer.getEntry(event);
    const int n_jets = buffer.n_jets;
    total_jets += n_jets;
    for (int jidx = 0; jidx < n_jets; jidx++) {
      Jet jet(buffer, jidx);
      float abs_eta = std::abs(jet.eta);
      bool ok_jvf = jet.jvf > 0.5 || abs_eta > 2.4 || jet.pt > 50e3;
      if (jet.pt < 20e3 || abs_eta > 2.5 || !ok_jvf) continue;
      hists.fill(jet, 1.0);
    }
  }
  if (test) buffer.saveSetBranches("required_branches.txt");
  if (test) printf("done event loop, saving\n");
  H5::H5File out_file(out_name.c_str(), H5F_ACC_EXCL);
  hists.writeTo(out_file);

  return 0;
}

