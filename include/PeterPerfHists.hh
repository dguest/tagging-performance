#ifndef PETER_PERF_HISTS_HH
#define PETER_PERF_HISTS_HH

class Histogram;
class Jet;
class TagTriple;
namespace H5 {
  class CommonFG;
}

#include <vector>
#include <map>
#include <cstddef>		// size_t

namespace peter {
  const int N_BINS = 10000;
  const int N_2AX_BINS = 2000;
  const double GAIA_LOW = -10.0;
  const double GAIA_HIGH = 10.0;

  const float JFC_ANTI_B_MIN = -0.9;
  const float JFC_ANTI_U_MIN =  0.95;

  class PtEfficiency {
  public:
    PtEfficiency(float antib, float antiu);
    ~PtEfficiency();
    PtEfficiency(PtEfficiency&) = delete;
    PtEfficiency& operator=(PtEfficiency&) = delete;
    void fill(float pt, const TagTriple&, double weight);
    void writeTo(H5::CommonFG&);
  private:
    Histogram* m_pass;
    Histogram* m_fail;
    float m_anti_b;
    float m_anti_u;
  };

  class Hists {
  public:
    Hists();
    ~Hists();
    Hists(Hists&) = delete;
    Hists& operator=(Hists&) = delete;
    void fill(const Jet&, double weight);
    void writeTo(H5::CommonFG&);
  private:
    PtEfficiency m_jfc_efficiency;
    Histogram* m_jfc;
    Histogram* m_jfit;
  };

  class FlavoredHists {
  public:
    FlavoredHists(unsigned flags = 0);
    ~FlavoredHists();
    FlavoredHists(FlavoredHists&) = delete;
    FlavoredHists& operator=(FlavoredHists&) = delete;
    void fill(const Jet&, double weight);
    void writeTo(H5::CommonFG&);
  private:
    std::vector<Hists> m_flavors;
  };
}
#endif
