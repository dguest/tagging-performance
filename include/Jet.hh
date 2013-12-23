#ifndef JET_ITER_HH
#define JET_ITER_HH

#include <cstddef>

class TreeBuffer; 
class TagVectors; 

struct TagTriple { 
  TagTriple(); 
  TagTriple(const TagVectors&, int index); 
  float pu; 
  float pc; 
  float pb; 
};

struct Jet { 
  Jet(); 
  Jet(const TreeBuffer&, int index); 
  int event; 
  float pt; 
  float eta; 
  bool valid; 
  float mv1; 
  float mv1c; 
  float mv2c00; 
  float mv2c10; 
  float mv2c20; 
  float mvb; 
  int truth_label; 
  TagTriple gaia; 
  TagTriple jfit; 
  TagTriple jfc; 
}; 


#endif
