from openreality.sdk.config import ConfigParser

parser = ConfigParser(file="config.toml")
print(parser.config)
