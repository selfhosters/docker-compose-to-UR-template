# docker-compose-to-UR-template

Reads a docker-compose file and translates volumes, ports and enviroment variables into a Unraid compatible template

WIP - Tested on a very small selection of compose-files

## Usage
### Docker (preferred)
 ````shell script
docker run -v "/home/roxedus/templater:/app/data" -v "/home/roxedus/docker-compose.yml:/app/data/docker-compose.yml" roxedus/compose-templater:master
````

### Manual
git clone the repository. install requirements  
Place your compose in data/ so it looks like docker/docker-compose.yml  
Run either Converter.py or CLI.py. Converter.py is basically `CLI.py -a`