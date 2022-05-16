# CBIM-position
This is the repository to host the CBIM Ontology and the related enrichment procedure

### Reference publication

*Reference to the CBIM position paper TBD*

## CBIM Ontology

Two ontology files can be found under the folder "[CBIM Ontology](<https://github.com/terry-oy/CBIM-position/tree/main/CBIM Ontology>)": 

1. [CBIM-Ontology-full.owl](<https://github.com/terry-oy/CBIM-position/blob/main/CBIM Ontology/CBIM-Ontology-full.owl>): the full version of the CBIM Ontology in consistent with the one presented in the paper.

2. [CBIM-Ontology-simple.owl](<https://github.com/terry-oy/CBIM-position/blob/main/CBIM Ontology/CBIM-Ontology-simple.owl>): a simplified version of the CBIM Ontology evolved from the original full Ontology. 

## Enriching multidisciplinary BIM graphs with CBIM relationships

Users are encouraged to replicate the enrichment procedure demonstrated in [Playground.ipynb](https://github.com/terry-oy/CBIM-position/blob/main/Playground.ipynb).

The inputs to the enrichment procedure are:

1. [ms_arc_LBD.ttl](https://github.com/terry-oy/CBIM-position/blob/main/ms_arc_LBD.ttl), the raw LBD representation of the architectural partial model.
2. [ms_str_LBD.ttl](https://github.com/terry-oy/CBIM-position/blob/main/ms_str_LBD.ttl), the raw LBD representation of the structural partial model.
3. [ms_plum_LBD.ttl](https://github.com/terry-oy/CBIM-position/blob/main/ms_plum_LBD.ttl), the raw LBD representation of the pluming partial model.

The final product of the enrichment procedure is [enriched_ms_metagraph.trig](https://github.com/terry-oy/CBIM-position/blob/main/enriched_ms_metagraph.trig), the combined meta-graph with enriched CBIM relationships established between building objects across domains.

