#include "buildHists.hh"
#include "RunConfig.hh"

int main(int narg, char* argv[]) {
  RunConfig config(narg, argv);
  return buildHists(config.files, config.out_name, config.flags);
}

