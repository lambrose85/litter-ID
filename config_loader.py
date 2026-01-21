# config_loader.py (optional but clean)
import yaml
from typing import Dict, Any

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML config file
        
    Returns:
        Dictionary containing all configuration
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Config loaded from {config_path}")
        return config
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        print("📝 Creating default config...")
        return create_default_config()
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML: {e}")
        raise

def create_default_config() -> Dict[str, Any]:
    """Create and save a default configuration"""
    default_config = {
        "camera": {"device_id": 0},
        "detection": {"history": 500, "dist_threshold": 400},
        "litter_box": {"x1_percent": 0.3, "y1_percent": 0.4}
    }
    
    # Save it for next time
    with open("config.yaml", 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    print("📄 Default config.yaml created")
    return default_config