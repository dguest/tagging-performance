#ifndef JET_HH
#define JET_HH

#include <cstddef>
#include <stdexcept>

class TreeBuffer;
class PetersBuffer;
class TagVectors;
class TagArrays;

enum class Flavor {B, C, U, T, DATA, ERROR};

struct TagTriple {
  TagTriple();
  TagTriple(const TagVectors&, int index);
  TagTriple(const TagArrays&, int index);
  bool allNonzero() const;
  float pu;
  float pc;
  float pb;
};

struct Jet {
  Jet();
  Jet(const TreeBuffer&, int index);
  Jet(const PetersBuffer&, int index);
  int event;
  float pt;
  float eta;
  float jvf;
  bool valid;
  float mv1;
  float mv1c;
  float mv2c00;
  float mv2c10;
  float mv2c20;
  float mvb;
  Flavor truth_label;
  TagTriple gaia;
  TagTriple jfit;
  TagTriple jfc;
  bool gaia_valid;
private:
  Flavor getFlavor(int);
};


class BadJetError: public std::range_error
{
public:
  BadJetError(const std::string& problem);
};


#endif
