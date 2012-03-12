pushd ../../../static/prov-o-diagrams
   # Diagrams
   curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/core.png
   curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/Qualified-Association.png
   curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/involvements.png
popd

touch beforefetch
curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/examples/eg-9-provrdf-owl-coverage/rdf/create/rdf/eg-9-provrdf-owl-coverage.html.ttl
# Examples
curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/eg16-journalism-qualified-association.ttl
curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/eg16-journalism-qualified-derivation.ttl
curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/eg16-journalism-qualified-generation.ttl
curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/eg16-journalism-qualified-usage.ttl
curl -O http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/khalid-jun-dropbox/eg16-journalism-simple-without-comments.ttl

for ttl in `find . -name "*.ttl" -newer beforefetch`; do
   cat $ttl | sed 's/</\&lt;/g; s/>/\&gt;/g' > b
   mv b $ttl
done
rm beforefetch
