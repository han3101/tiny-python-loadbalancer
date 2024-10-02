import json
from cerberus import Validator
import os


def load_config() -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, '..', 'config.json')
    with open(config_file) as f:
        config = json.load(f)

    return config

class lbAlgorithm:
    ROUND_ROBIN = 'round-robin'
    IP_HASH = 'ip-hash'
    WEIGHTED_ROUND_ROBIN = 'weighted-round-robin'

def config_to_lbAlgorithm(lb_method: str) -> str:
    if lb_method == 'round-robin':
        return lbAlgorithm.ROUND_ROBIN
    elif lb_method == 'ip-hash':
        return lbAlgorithm.IP_HASH
    elif lb_method == 'weighted-round-robin':
        return lbAlgorithm.WEIGHTED_ROUND_ROBIN
    else:
        raise ValueError(f"[ConfigError] Unknown lb_method: {lb_method}, must be one of 'round-robin', 'ip-hash', 'weighted-round-robin'")

# Validation schema for config.json
config_schema = {
    'upstream': {
        'type': 'list', 'minlength': 1,
        'schema': {
            'type': 'dict',
            'schema': {
                'domain': {'type': 'string', 'required': True},
                'weight': {'type': 'integer', 'min': 1, 'nullable': True}
            }
        }
    },
    'lb_method': {'type': 'string', 'allowed': ['round-robin', 'ip-hash', 'weighted-round-robin', 'random'], 'required': True},
    'listen': {'type': 'integer', 'required': True},

    'retries': {'type': 'integer', 'min': 0, 'required': True},
    'connect_timeout': {'type': 'integer', 'min': 0, 'max': 10000, 'required': False},
    'read_timeout': {'type': 'integer', 'min': 0, 'max': 10000, 'required': False},
    'send_timeout': {'type': 'integer', 'min': 0, 'max': 10000, 'required': False},
    'next_timeout': {'type': 'integer', 'min': 0, 'max': 10000, 'required': False},

    'health_check_path': {'type': 'string', 'required': True},
    'health_check_timeout': {'type': 'integer', 'min': 0, 'max': 10, 'required': True},
    'health_check_fails': {'type': 'integer', 'min': 0, 'required': True},
    'health_check_pass': {'type': 'integer', 'min': 0, 'max': 10, 'required': True},
    'health_check_interval': {'type': 'integer', 'min': 0, 'max': 300 * 1000, 'required': True},

    'send_alert_webhook': {'type': 'string', 'required': False, 'nullable': True, 'default': False},
    'alert_on_failure_streak': {'type': 'integer', 'min': 1, 'max': 100, 'required': False, 'default': 3},

    'enableSelfHealing': {'type': 'boolean', 'required': True}
}

# Validate the config using Cerberus
def validate_config(config):
    v = Validator(config_schema)
    if not v.validate(config):
        raise ValueError(f"[ConfigError] {v.errors}")

    print("[Success] Validated Config")
    return True


# Function to initialize default values for missing fields
def initialize_config(config: dict) -> dict:
    # Assign default values if not present
    config['lb_method'] = config.get('lb_method', 'round-robin')
    config['listen'] = config.get('listen', 80)
    
    config['retries'] = config.get('retries', 3)
    config['connect_timeout'] = config.get('retry_interval', 5)
    config['read_timeout'] = config.get('retry_interval', 5)
    config['send_timeout'] = config.get('retry_interval', 5)
    config['next_timeout'] = config.get('retry_interval', 5)
    
    config['health_check_path'] = config.get('health_check_path', '/health')
    config['health_check_timeout'] = config.get('health_check_timeout', 2)
    config['health_check_fails'] = config.get('health_check_fails', 3)
    config['health_check_pass'] = config.get('health_check_pass', 2)
    config['health_check_interval'] = config.get('health_check_interval', 10)
    
    config['alert_on_failure_streak'] = config.get('alert_on_failure_streak', 3)
    config['enableSelfHealing'] = config.get('enableSelfHealing', False)

    return config


# debug
def get_config():
    # Load the configuration from file
    config = load_config()

    # Initialize with default values if not present
    config = initialize_config(config)

    # Validate the configuration
    validate_config(config)

    # Map the lb_method to the internal representation
    config['lbAlgo'] = config_to_lbAlgorithm(config['lb_method'])

    print(config)
    print("[Success] Loaded Config")

    return config

# get_config()