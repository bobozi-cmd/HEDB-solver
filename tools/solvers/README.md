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

