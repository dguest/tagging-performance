#include "fillPetersHists.hh"
#include "RunConfig.hh"

int main(int narg, char* argv[]) {
  RunConfig config(narg, argv);
  return fillPetersHists(config.files, config.out_name, config.flags);
}
