# How to use hedb-solver (docker)

## Get Start
```bash
cd HEDB-solver
# stop hedb container
docker stop $(docker ps -q --filter ancestor=hedb-solver)

docker build -t hedb-solver .
cd ..
docker run --privileged -d --rm \
        -v ./HEDB-solver:/home/ubuntu/HEDB-solver \
        --name hedb-solver-$(whoami) -p 2222:22 hedb-solver
# passwd: 1234
ssh -o StrictHostKeyChecking=no -p 2222 ubuntu@localhost
```

## Build
```bash
# in docker
cd HEDB-solver
sudo service postgresql restart
make clean

make
make install
make run
make stop
```

## Test HEDB
```bash
sudo -u postgres psql
> ALTER USER postgres WITH PASSWORD 'postgres';
> DROP EXTENSION IF EXISTS hedb CASCADE;
> CREATE EXTENSION hedb;
> SELECT enable_client_mode();
> SELECT '1024'::enc_int4 * '4096'::enc_int4;
```

## Smuggle
```bash
make run

sudo -u postgres psql
> ALTER USER postgres WITH PASSWORD 'postgres';
cd HEDB-solver/tests/tpch
python3 run.py -l

make stop
rm /tmp/integrity_zone.log
rm /tmp/privacy_zone.log
make run

cd HEDB-solver/tools
python3 smuggle.py
cp /tmp/integrity_zone.log ./solvers
cp /tmp/privacy_zone.log ./solvers

sudo chown ubuntu ./solvers/integrity_zone.log
sudo chown ubuntu ./solvers/privacy_zone.log
```


## Use solver
```bash
cd HEDB-solver/tools/solvers
# generate sql's trace
python3 main.py trace -q ../../tests/tpch/secure-query/ -t ./trace
# analysis Q5.log, and print ops distribution
python3 main.py analysis -l ./trace/Q5.log

# trace_translator.py is a demo to parser a *.tr to generator a set of formulas
# There are 2 formal can be supported:
#       unary formula : y9 == 23
#       binary formula: ( y8 + x10 ) == y9
# and // marks comments
python3 ./trace_translator.py -s {sat_trace}.tr -u {unsat_trace}.tr 
```