apt-get install maven -qq
git clone https://github.com/castorini/anserini.git
cd anserini
mvn clean package appassembler:assemble -DskipTests -Dmaven.javadoc.skip=true
cd eval && tar xvfz trec_eval.9.0.4.tar.gz && cd trec_eval.9.0.4 && make
