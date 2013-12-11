#!/bin/bash

echo "********************************************************************************"
echo "********************************************************************************"
echo "********************************************************************************"
echo ""
echo "				    STARTING..."
echo""
echo "********************************************************************************"
echo ""
echo "********************************************************************************"
echo ""
echo "				 Preparing terms to tag... "
echo ""
cat FSOVabstract_term_lemma_head.csv| awk -F'\t' '{print $1"\t"$3}' | tr [A-Z] [a-z] | sort -u > heads_totag
echo "********************************************************************************"
echo ""
echo "				 Preparing resources (onto in OBO, onto heads, flat dictionnairies)... "
echo ""
cp plant_property_part.v15 onto
cat PLANT_PROPERTY_candidates_term_lemma_head.txt | awk -F'\t' '{print $1"\t"$3}' | tr [A-Z] [a-z] >heads_tolearn_onto
echo "********************************************************************************"
echo ""
echo "				 Preparing lemmas from terms to tag (term\tlemma) in the file lemma... "
echo ""
cat FSOVabstract_term_lemma_head.csv| awk -F'\t' '{print $1"\t"$2}' | tr [A-Z] [a-z] | sort -u > lemma
cat FSOVabstract_term_lemma_head.csv| awk -F'\t' '{print $3"\t"$3}' | tr [A-Z] [a-z] | sort -u >> lemma

echo "********************************************************************************"
echo ""
echo "				 Preparing lemmas from resources (onto) in the same file (lemma)... "
echo ""
cat PLANT_PROPERTY_candidates_term_lemma_head.txt | awk -F'\t' '{print $1"\t"$2}' | tr [A-Z] [a-z] | sort -u >> lemma
cat PLANT_PROPERTY_candidates_term_lemma_head.txt | awk -F'\t' '{print $3"\t"$3}' | tr [A-Z] [a-z] | sort -u >> lemma
sort -u lemma > tmp && mv tmp lemma
echo "********************************************************************************"
echo ""
echo "				 Preparing lemma cs for post-processing (pour_la_princesse)... "
echo ""
cat FSOVabstract_term_lemma_head.csv | awk -F'\t' '{print $1"\t"$2}' | sort -u > lemma_cs
cat FSOVabstract_term_lemma_head.csv | awk -F'\t' '{print $3"\t"$3}' | sort -u >> lemma_cs
cat PLANT_PROPERTY_candidates_term_lemma_head.txt | awk -F'\t' '{print $1"\t"$2}' | sort -u >> lemma_cs
cat PLANT_PROPERTY_candidates_term_lemma_head.txt | awk -F'\t' '{print $3"\t"$3}' | sort -u >> lemma_cs
echo "********************************************************************************"
echo ""
echo "				 REMINDER : Checking of blacklist and GHOST in onto... "
echo ""
echo "Do you have an updated blacklist ???"
echo "Have you added the GHOST to onto ???"
echo "********************************************************************************"
echo "********************************************************************************"
