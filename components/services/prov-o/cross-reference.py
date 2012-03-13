#!/usr/bin/env python

# To install dependencies, see https://github.com/timrdf/DataFAQs/wiki/Errors

import sys
from rdflib import *

from surf import *
from surf.query import a, select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor, 'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,    'rdfextras.sparql.query',     'SPARQLQueryResult')

if len(sys.argv) != 4:
   print "usage: cross-reference.py http://some.owl someont.owl prefix"
   print
   print "  http://some.owl      - web URL of the OWL e.g. http://dvcs.w3.org/hg/prov/raw-file/default/ontology/ProvenanceOntology.owl"
   print "  some.owl             - local copy of the OWL e.g. ProvenanceOntology.owl"
   print "  prefix               - prefix to use e.g. 'prov'"
   sys.exit(1)

ont_url   = sys.argv[1] # http://dvcs.w3.org/hg/prov/raw-file/default/ontology/ProvenanceOntology.owl
ont_local = sys.argv[2] # ProvenanceOntology.owl
PREFIX    = sys.argv[3] # prov

ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(void='http://rdfs.org/ns/void#')

prefixes = dict(prov=str(ns.PROV), dcat=str(ns.DCAT), void=str(ns.VOID))

# as rdflib
graph = Graph()
graph.parse(ont_local) # from file

# as SuRF
store = Store(reader='rdflib', writer='rdflib', rdflib_store = 'IOMemory') 
session = Session(store)
store.load_triples(source=ont_url) # From URL
DatatypeProperties = session.get_class(ns.OWL["DatatypeProperty"])
ObjectProperties   = session.get_class(ns.OWL["ObjectProperty"])
Classes            = session.get_class(ns.OWL["Class"])

qualifiedFormsQ = '''
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix prov: <http://www.w3.org/ns/prov#>

select distinct ?unqualified ?qualified ?involvement
where {
   graph <http://www.w3.org/ns/prov#> {

      ?unqualified prov:qualifiedForm []; prov:category "CATEGORY" .

      optional {
         ?unqualified prov:qualifiedForm ?qualified .
                                         ?qualified a owl:ObjectProperty
      }

      optional {
         ?unqualified prov:qualifiedForm ?involvement .
                                         ?involvement a owl:Class
      }
   }
} order by ?unqualified
'''

results = graph.query('select distinct ?cat where { [] prov:category ?cat } order by ?cat', initNs=prefixes)
categories = {}
for bindings in results:
   categories[bindings] = True # distinct operator is not being recognized. Need to reimplement here.
for category in categories.keys():
   print category

   glanceName    = 'at-a-glance-'+category+'.html'
   crossName     = 'cross-reference-'+category+'.html'
   qualsName = 'qualifed-forms-'+category+'.html'
   if not(os.path.exists(glanceName)) and not(os.path.exists(crossName)) and not(os.path.exists(qualsName)):
      print '  '+glanceName + ' ' + crossName
      glance = open(glanceName, 'w')
      cross  = open(crossName, 'w')
      quals = open(qualsName, 'w')

      # Classes # # # # # # # # # # # # # # # # #
      glance.write('\n')
      glance.write('<div    id="'+PREFIX+'-'+category+'-owl-classes-at-a-glance"\n')
      glance.write('     class="'+PREFIX+'-'+category+' owl-classes at-a-glance">\n')
      glance.write('  <ul class="hlist">\n')

      ordered = {}
      ordered['classes'] = []
      for owlClass in Classes.all():
         if owlClass.prov_category.first == category:
            ordered['classes'].append(owlClass.subject)
      ordered['classes'].sort()

      # at-a-glance
      for uri in ordered['classes']:
         owlClass = session.get_resource(uri,Classes)
         qname = owlClass.subject.split('#')
         glance.write('    <li>\n')
         glance.write('      <a href="#'+qname[1]+'">'+PREFIX+':'+qname[1]+'</a>\n')
         glance.write('    </li>\n')
      glance.write('  </ul>\n')
      glance.write('</div>\n')


      # Properties # # # # # # # # # # # # # # # # #
      glance.write('\n')
      glance.write('<div    id="'+PREFIX+'-'+category+'-owl-properties-at-a-glance"\n')
      glance.write('     class="'+PREFIX+'-'+category+' owl-properties at-a-glance">\n')
      glance.write('  <ul class="hlist">\n')

      propertyTypes = {}
      ordered['properties'] = []
      for property in DatatypeProperties.all():
         if property.prov_category.first == category:
            ordered['properties'].append(property.subject)
            propertyTypes[property.subject] = "datatype-property"
      for property in ObjectProperties.all():
         if property.prov_category.first == category:
            ordered['properties'].append(property.subject)
            propertyTypes[property.subject] = "object-property"
      ordered['properties'].sort()

      # at-a-glance
      for uri in ordered['properties']:
         property = []
         if propertyTypes[uri] == 'datatype-property':
            property = session.get_resource(uri,DatatypeProperties)
         else:
            property = session.get_resource(uri,ObjectProperties)
         qname = property.subject.split('#')
         glance.write('    <li class="'+propertyTypes[uri]+'">\n')
         glance.write('      <a href="#'+qname[1]+'">'+PREFIX+':'+qname[1]+'</a>\n')
         glance.write('    </li>\n')
      glance.write('  </ul>\n')
      glance.write('</div>\n')


      # Classes # # # # # # # # # # # # # # # # #
      # cross-reference
      cross.write('<div    id="'+PREFIX+'-'+category+'-owl-classes-crossreference"\n')
      cross.write('     class="'+PREFIX+'-'+category+' owl-classes crossreference">\n')
      for uri in ordered['classes']:
         owlClass = session.get_resource(uri,Classes)
         qname = owlClass.subject.split('#')
         cross.write('\n')
         cross.write('  <div id="'+qname[1]+'" class="entity">\n')
         cross.write('    <h3>\n')
         cross.write('      <a href="#'+qname[1]+'"><span class="dotted" title="'+uri+'">'+PREFIX+':'+qname[1]+'</span></a>\n')
         cross.write('      <span class="backlink">\n')
         #cross.write('         back to <a href="#toc">ToC</a> or\n')
         cross.write('         back to <a href="#'+PREFIX+'-'+category+'-owl-classes-at-a-glance">'+category+' classes</a>\n')
         cross.write('      </span>\n')
         cross.write('    </h3>\n')

         # class
         cross.write('    <p><strong>IRI:</strong>'+uri+'</p>\n')

         # class rdfs:comment
         for comment in owlClass.rdfs_comment:
            cross.write('    <div class="comment"><p>'+comment+'</p>\n')
            cross.write('    </div>\n')
         cross.write('    <dl class="description">\n')

         # class rdfs:subClassOf ?super
         if len(owlClass.rdfs_subClassOf) > 0:
            cross.write('      <dt>is subclass of</dt>\n')
            cross.write('      <dd>\n')
            for super in owlClass.rdfs_subClassOf:
               qname = super.subject.split('#')
               cross.write('        <a title="'+super.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
            cross.write('      </dd>\n')

         # ?p rdfs:domain class
         if len(owlClass.is_rdfs_domain_of) > 0:
            cross.write('      <dt>is in domain of</dt>\n')
            cross.write('      <dd>\n')
            for p in owlClass.is_rdfs_domain_of:
               pqname = p.subject.split('#')
               cross.write('        <a title="'+p.subject+'" href="#'+pqname[1]+'">'+PREFIX+':'+pqname[1]+'</a>\n')
               if ns.OWL['DatatypeProperty'] in p.rdf_type:
                  cross.write('        <sup class="type-dp" title="data property">dp</sup>\n')
               else:
                  cross.write('        <sup class="type-op" title="object property">op</sup>\n')
            cross.write('      </dd>\n')

         # ?p rdfs:range class
         if len(owlClass.is_rdfs_range_of) > 0:
            cross.write('      <dt>is in range of</dt>\n')
            cross.write('      <dd>\n')
            for p in owlClass.is_rdfs_range_of:
               pqname = p.subject.split('#')
               cross.write('        <a title="'+p.subject+'" href="#'+pqname[1]+'">'+PREFIX+':'+pqname[1]+'</a>\n')
               if ns.OWL['DatatypeProperty'] in p.rdf_type:
                  cross.write('        <sup class="type-dp" title="data property">dp</sup>\n')
               else:
                  cross.write('        <sup class="type-op" title="object property">op</sup>\n')
            cross.write('      </dd>\n')

         # ?sub rdfs:subClassOf class
         if len(owlClass.is_rdfs_subClassOf_of) > 0:
            es = ''
            if len(owlClass.is_rdfs_subClassOf_of) > 1:
               es="es"
            cross.write('      <dt>has subclass'+es+'</dt>\n')
            cross.write('      <dd>\n')
            for sub in owlClass.is_rdfs_subClassOf_of:
               qname = sub.subject.split('#')
               cross.write('        <a title="'+sub.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
            cross.write('      </dd>\n')

         cross.write('    </dl>\n')
         cross.write('  </div>\n')
      cross.write('</div>\n')


      # Properties # # # # # # # # # # # # # # # # #
      # cross-reference
      cross.write('<div    id="'+PREFIX+'-'+category+'-owl-properties-crossreference"\n')
      cross.write('     class="'+PREFIX+'-'+category+' owl-properties crossreference">\n')
      for uri in ordered['properties']:
         property = []
         if propertyTypes[uri] == 'datatype-property':
            property = session.get_resource(uri,DatatypeProperties)
         else:
            property = session.get_resource(uri,ObjectProperties)
         qname = property.subject.split('#')
         cross.write('  <div id="'+qname[1]+'" class="entity">\n')
         cross.write('    <h3>\n')
         cross.write('      <a href="#'+qname[1]+'"><span class="dotted" title="'+uri+'">'+PREFIX+':'+qname[1]+'</span></a>\n')
         if ns.OWL['DatatypeProperty'] in property.rdf_type:
            cross.write('      <sup class="type-dp" title="data property">dp</sup>\n')
         else:
            cross.write('      <sup class="type-op" title="object property">op</sup>\n')
         cross.write('      <span class="backlink">\n')
         cross.write('         back to <a href="#'+PREFIX+'-'+category+'-owl-properties-at-a-glance">'+category+' properties</a>\n')
         cross.write('      </span>\n')
         cross.write('    </h3>\n')

         # property
         cross.write('    <p><strong>IRI:</strong>'+uri+'</p>\n')

         cross.write('    <div class="description">\n')

         # class rdfs:comment
         for comment in property.rdfs_comment:
            cross.write('    <div class="comment"><p>'+comment+'</p>\n')
            cross.write('    </div>\n')

         # Characteristics
         characteristics = [ns.OWL['FunctionalProperty'],
                            ns.OWL['InverseFunctionalProperty'],
                            ns.OWL['TransitiveProperty'],
                            ns.OWL['SymmetricProperty'],
                            ns.OWL['AsymmetricProperty'],
                            ns.OWL['ReflexiveProperty'],
                            ns.OWL['IrreflexiveProperty']]
         has = False
         for characteristic in characteristics:
            if characteristic in property.rdf_type:
               has = True
         if has:
            cross.write('      <p><strong>has characteristics</strong>\n')
            comma = ''
            for characteristic in characteristics:
               if characteristic in property.rdf_type:
                  qname = characteristic.split('#')
                  cross.write(comma+' '+qname[1].replace('Property','').replace('F',' F')+'\n')
                  comma = ','
            cross.write('      </p>\n')

         cross.write('      <dl>\n')

         # property rdfs:subPropertyOf ?super
         do = False
         for super in property.rdfs_subPropertyOf:
            qname = super.subject.split('#')
            if qname[0] == 'http://www.w3.org/ns/prov':
               do = True
         if do:
            cross.write('      <dt>has super-properties</dt>\n')
            cross.write('      <dd>\n')
            cross.write('        <ul>\n')
            for super in property.rdfs_subPropertyOf:
               qname = super.subject.split('#')
               if qname[0] == 'http://www.w3.org/ns/prov':
                  cross.write('          <li>\n')
                  cross.write('            <a title="'+super.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
                  cross.write('          </li>\n')
            cross.write('        </ul>\n')
            cross.write('      </dd>\n')

         # property rdfs:domain ?class
         if len(property.rdfs_domain) > 0:
            cross.write('      <dt>has domain</dt>\n')
            cross.write('      <dd>\n')
            cross.write('        <ul>\n')
            for domain in property.rdfs_domain:
               qname = domain.subject.split('#')
               cross.write('          <li>\n')
               cross.write('            <a title="'+domain.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
               cross.write('          </li>\n')
            cross.write('        </ul>\n')
            cross.write('      </dd>\n')

         # property rdfs:range ?class
         if len(property.rdfs_range) > 0:
            cross.write('      <dt>has range</dt>\n')
            cross.write('      <dd>\n')
            cross.write('        <ul>\n')
            for range in property.rdfs_range:
               cross.write('          <li>\n')
               try:
                  qname = range.subject.split('#')
                  if qname[0] == 'http://www.w3.org/ns/prov':
                     cross.write('            <a title="'+range.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
                  elif qname[0] == 'http://www.w3.org/2002/07/owl':
                     noop = 'noop'
                  else:
                     cross.write('            '+str(range)+'\n')
               except:
                  cross.write('            '+str(range)+'\n')
               cross.write('          </li>\n')
            cross.write('        </ul>\n')
            cross.write('      </dd>\n')

         # property owl:inverseOf ?inverse
         if len(property.owl_inverseOf) > 0:
            cross.write('      <dt>has inverse</dt>\n')
            cross.write('      <dd>\n')
            cross.write('        <ul>\n')
            for inverse in property.owl_inverseOf:
               cross.write('          <li>\n')
               try:
                  qname = inverse.subject.split('#')
                  if qname[0] == 'http://www.w3.org/ns/prov':
                     cross.write('            <a title="'+inverse.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
                  elif qname[0] == 'http://www.w3.org/2002/07/owl':
                     noop = 'noop'
                  else:
                     cross.write('            '+str(inverse)+'\n')
               except:
                  cross.write('            '+str(inverse)+'\n')
               cross.write('          </li>\n')
            cross.write('        </ul>\n')
            cross.write('      </dd>\n')

         # ?sub rdfs:subPropertyOf property
         do = False
         for sub in property.is_rdfs_subPropertyOf_of:
            qname = sub.subject.split('#')
            if qname[0] == 'http://www.w3.org/ns/prov':
               do = True
         if do:
            cross.write('      <dt>has sub-properties</dt>\n')
            cross.write('      <dd>\n')
            cross.write('        <ul>\n')
            for sub in property.is_rdfs_subPropertyOf_of:
               qname = sub.subject.split('#')
               if qname[0] == 'http://www.w3.org/ns/prov':
                  cross.write('          <li>\n')
                  cross.write('            <a title="'+sub.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a>\n')
                  cross.write('          </li>\n')
            cross.write('        </ul>\n')
            cross.write('      </dd>\n')


         cross.write('      </dl>\n')

         cross.write('    </div>\n')
         cross.write('  </div>\n')
         cross.write('\n')
      cross.write('</div>\n')

      n = ''
      if category.lower()[0] == 'a':
         n = 'n'
      quals.write('<table class="qualified-forms">\n')
      quals.write('  <caption>Qualification Property and Involvement Class used to qualify a'+n+' '+category.capitalize()+' Property.</caption>\n')
      quals.write('  <tr>\n')
      qname = property.subject.split('#')
      quals.write('    <th>'+category.capitalize()+' Property</th>\n')
      quals.write('    <th>Qualification Property</th>\n')
      quals.write('    <th>Involvement Class</th>\n')
      quals.write('  </tr>\n')
      for uri in ordered['properties']:
         property = []
         if propertyTypes[uri] == 'datatype-property':
            property = session.get_resource(uri,DatatypeProperties)
         else:
            property = session.get_resource(uri,ObjectProperties)
         if len(property.prov_qualifiedForm) > 0:
            qualProp  = 'no'
            qualClass = 'no'
            for qualified in property.prov_qualifiedForm:
               if ns.OWL['ObjectProperty'] in qualified.rdf_type:
                  qualProp  = qualified 
               else:
                  qualClass = qualified 
            if qualProp != 'no' and qualClass != 'no':
               quals.write('  <tr>\n')
               qname = property.subject.split('#')
               quals.write('    <td><a title="'+property.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a></td>\n')
               qname = qualProp.subject.split('#')
               quals.write('    <td><a title="'+qualProp.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a></td>\n')
               qname = qualClass.subject.split('#')
               quals.write('    <td><a title="'+qualClass.subject+'" href="#'+qname[1]+'" class="owlclass">'+PREFIX+':'+qname[1]+'</a></td>\n')
               quals.write('  </tr>\n')
      quals.write('</table>\n')

      glance.close()
      cross.close()
      quals.close()
   else:
      print '  '+glanceName + ' or ' + crossName + " already exists. Not modifying."