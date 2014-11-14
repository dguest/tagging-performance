#include <vector>
#include <string>
#include <cstring>

struct RunConfig {
  RunConfig(int narg, char* argv[]);
  std::string out_name;
  unsigned flags;
  std::vector<std::string> files;
};

void usage(std::string call);
void help();
