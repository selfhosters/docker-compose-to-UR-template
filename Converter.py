import yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom

base = ET.Element('Container', attrib={'version': '2'})
base.append(ET.Comment("Generated with Selfhosters compose>template script"))


class ReadYAML:
    def __init__(self):
        with open('data/docker-compose.yml') as f:
            self.compose = yaml.load(f, Loader=yaml.FullLoader)
        with open('data/defaults.yml') as f:
            self.defaults = yaml.load(f, Loader=yaml.FullLoader)
        self.services = self._get_services(self)

    def list_field(self, service, field):
        decrim = {"environment": "=", "ports": ":", "volumes": ":"}
        fields = []
        try:
            for entries in self.compose['services'][service][field]:
                entries_list = []
                for entry in entries.split(decrim[field]):
                    entries_list.append(entry)
                fields.append(entries_list)
            return fields
        except KeyError:
            print(f"{field} is not present, skipping")

    def list_data(self, service, field):
        return self.compose['services'][service][field]

    def load_defaults(self, field):
        return self.defaults['branding'][field]

    @staticmethod
    def _get_services(self):
        _services = {}
        ind = 0
        if not _services:
            for service in self.compose['services']:
                _services[ind] = service
                ind += 1
            return _services
        elif _services:
            return _services
        else:
            print("FATAL ERROR")


class Generator:
    def __init__(self, service):
        self.elem = base
        self.service = service
        self.reader = ReadYAML()
        self.gen = GenXML(service)

    def write(self):
        self.gen.write()

    def variable(self, **kwargs2: {}):
        kwargs = {}
        fields = self.reader.list_field(self.service, "environment")
        if fields:
            for name, value in fields:
                if name == "TZ":
                    continue

                best_guess = {"Name": {"PUID": {"Target": "100", "Display": "advanced-hide", "Required": "true"},
                                       "PGID": {"Target": "99", "Display": "advanced-hide", "Required": "true"}},
                              "should_mask": {"password": {"Mask": "true"}}, "token": {"Mask": "true"}
                              }
                try:
                    for names in best_guess["Name"][name]:
                        kwargs[names] = best_guess["Name"][name][names]
                except KeyError:
                    pass
                try:
                    for i in best_guess["should_mask"]:
                        if i.lower() in name.lower():
                            kwargs["Mask"] = "true"
                except KeyError:
                    pass

                kwargs = {**kwargs, **kwargs2}
                GenXML.variable(self, name, value, **kwargs)
            return self.elem

    def network(self, **kwargs2: {}):
        kwargs = {}
        ports = self.reader.list_field(self.service, "ports")
        if ports:
            for host, container in ports:
                best_guess = {"Port": {"80": {"Name": "WebUI", "type": "port"}, "8080": {"Name": "WebUI", "type": "port"}}}
                try:
                    container, proto = container.split("/")
                    kwargs["Protocol"] = proto
                except ValueError:
                    pass
                try:
                    kwargs["Name"] = best_guess["Port"][container]["Name"]
                except KeyError:
                    pass
                kwargs = {**kwargs, **kwargs2}
                GenXML.networking(self, host, container,  **kwargs)
            return self.elem

    def data(self, **kwargs2: {}):
        best_guess = {"Target":
                      {"/config": {"Display": "always-hide", "type": "Path", "Required": "true",
                                   "Default": f"/mnt/user/appdata/{self.service}",
                                   "Name": "Appdata"}}}
        volumes = self.reader.list_field(self.service, "volumes")
        for n in range(len(volumes)):
            kwargs = {}
            host, container, *vargs = volumes[n]
            try:
                kwargs = best_guess["Target"][container]
            except KeyError:
                pass
            if vargs:
                kwargs["Mode"] = vargs[0]
            kwargs = {**kwargs, **kwargs2}
            GenXML.data(self, host, container, **kwargs)
        return self.elem

    def advanced(self, **kwargs: {}):
        try:
            kwargs["command"] = self.reader.list_data(self.service, "command")
        except KeyError:
            pass
        GenXML.advanced(self, **kwargs)

    def metadata(self, **kwargs2: {}):
        kwargs = {}
        kwargs["name"] = self.reader.list_data(self.service, "container_name")
        kwargs["repository"] = self.reader.list_data(self.service, "image")
        kwargs["registry"] = f"https://hub.docker.com/r/{kwargs['repository'].split(':')[0]}"
        kwargs["templateurl"] = self.reader.load_defaults("TemplateURLPrefix") + kwargs["name"] + ".xml"
        kwargs["icon"] = self.reader.load_defaults("IconPrefix") + kwargs["name"] + ".png"

        kwargs = {**kwargs, **kwargs2}
        GenXML.metadata(self, **kwargs)


class GenXML:
    conf_list = []

    def __init__(self, service):
        self.elem = base
        self.service = service
        self.name = "output2"

    def write(self):
        self._write(self.elem)

    def variable(self, name, value, **kwargs):
        env = ET.SubElement(self.elem, 'Environment')
        variable = ET.SubElement(env, 'Variable')
        ET.SubElement(variable, 'Name').text = name
        ET.SubElement(variable, 'Value')
        ET.SubElement(variable, 'Mode')
        atr = {"Name": kwargs.get("Name", name),
               "Target": kwargs.get("Target", value),
               "Default": kwargs.get("Default", value),
               "Mode": kwargs.get("Mode", ""),
               "Description": kwargs.get("Description", f"Container Variable: {name}"),
               "Type": "Variable",
               "Display": kwargs.get("Display", "always"),
               "Required": kwargs.get("Required", "false"),
               "Mask": kwargs.get("Mask", "false")}
        GenXML.conf_list.append(atr)
        return self.elem

    def networking(self, host, container, **kwargs):
        ET.SubElement(self.elem, 'Network').text = "bridge"
        net = ET.SubElement(self.elem, 'Networking')
        ET.SubElement(net, 'Mode').text = "bridge"
        variable = ET.SubElement(net, 'Publish')
        ET.SubElement(variable, 'HostPort').text = host
        ET.SubElement(variable, 'ContainerPort').text = container
        ET.SubElement(variable, 'Protocol').text = kwargs.get("Protocol", "tcp")
        atr = {"Name": kwargs.get("Name", "tcp"),
               "Target": kwargs.get("Target", container),
               "Default": kwargs.get("Default", host),
               "Mode": kwargs.get("Protocol", "tcp"),
               "Description": kwargs.get("Description", f"Container Port: {container}"),
               "Type": "Port",
               "Display": kwargs.get("Display", "always"),
               "Required": kwargs.get("Required", "false"),
               "Mask": kwargs.get("Mask", "false")}
        GenXML.conf_list.append(atr)
        return self.elem

    def data(self, host, container, **kwargs):
        vol = ET.SubElement(self.elem, 'Data')
        variable = ET.SubElement(vol, 'Volume')
        ET.SubElement(variable, 'HostDir')
        ET.SubElement(variable, 'ContainerDir').text = container
        ET.SubElement(variable, 'Mode').text = kwargs.get("Mode", "rw")
        atr = {"Name": kwargs.get("Name", f"Container path {container}"),
               "Target": kwargs.get("Target", container),
               "Default": kwargs.get("Default", host),
               "Mode": kwargs.get("Protocol", "rw"),
               "Description": kwargs.get("Description", f"Container Path: {container}"),
               "Type": "Path",
               "Display": kwargs.get("Display", "always"),
               "Required": kwargs.get("Required", "false"),
               "Mask": kwargs.get("Mask", "false")}
        GenXML.conf_list.append(atr)
        return self.elem

    def advanced(self, **kwargs):
        ET.SubElement(self.elem, 'PostArgs').text = kwargs.get("command", "")

    def metadata(self, **kwargs):
        self.name = kwargs.get("name", "SomeString")
        ET.SubElement(self.elem, 'TemplateURL').text = kwargs.get("templateurl", "SomeString")
        ET.SubElement(self.elem, 'Name').text = kwargs.get("name", "SomeString")
        ET.SubElement(self.elem, 'Repository').text = kwargs.get("repository", "SomeString")
        ET.SubElement(self.elem, 'Registry').text = kwargs.get("registry", "SomeString")
        ET.SubElement(self.elem, 'Project').text = kwargs.get("project", "SomeString")
        ET.SubElement(self.elem, 'Icon').text = kwargs.get("icon", "SomeString")
        ET.SubElement(self.elem, 'BindTime').text = kwargs.get("bindtime", "true")
        ET.SubElement(self.elem, 'Privileged').text = kwargs.get("privileged", "false")
        ET.SubElement(self.elem, 'Overview').text = kwargs.get("overview", "SomeString")
        ET.SubElement(self.elem, 'Description').text = kwargs.get("description", "SomeString")

    def _write(self, elem):
        for atr in self.conf_list:
            ET.SubElement(elem, 'Config', attrib=atr)
        xml_string = minidom.parseString(ET.tostring(elem)).toprettyxml(indent="   ")
        my_file = open(f"data/{self.service}.xml", "w")
        my_file.write(xml_string)
        print(f"{self.service} Created\n")


def run():
    services = ReadYAML().services
    for service in services:
        elm = Generator(services[service])
        elm.metadata()
        elm.advanced()
        elm.variable()
        elm.network()
        elm.data()
        GenXML(services[service])._write(elm.elem)


if __name__ == '__main__':
    run()
