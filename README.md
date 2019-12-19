# docker-compose-to-UR-template

Reads a docker-compose file and translates volumes, ports and enviroment variables into a Unraid compatible template

WIP - Tested on a very small selection of compose-files

## Usage
### Docker (preferred)
#### Prep the enviroment
````shell script
mkdir "templater"
wget -O $(pwd)/templater/defaults.yml https://raw.githubusercontent.com/selfhosters/docker-compose-to-UR-template/master/data/defaults.yml
````
Place a docker-compose.yml file in the new /templater dir

#### Run the container
 ````shell script
docker run -v "$(pwd)/templater:/app/data" roxedus/compose-templater:master
````

### Manual
git clone the repository. install requirements  
Place your compose in data/ so it looks like docker/docker-compose.yml  
Run either Converter.py or CLI.py. Converter.py is basically `CLI.py -a`