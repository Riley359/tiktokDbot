"""Setup script for Discord bot configuration."""

import os
import shutil

def setup_bot_config():
    """Setup bot configuration file."""
    config_example = "bot_config_example.py"
    config_file = "bot_config.py"
    
    if not os.path.exists(config_file):
        if os.path.exists(config_example):
            shutil.copy(config_example, config_file)
            print(f"✅ Created {config_file} from example")
            print(f"📝 Please edit {config_file} and add your Discord bot token")
        else:
            print(f"❌ {config_example} not found")
    else:
        print(f"✅ {config_file} already exists")

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        "discord.py",
        "TikTokApi",
        "requests", 
        "aiohttp",
        "playwright"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace(".py", "").replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def main():
    """Main setup function."""
    print("🤖 Discord TikTok Bot Setup")
    print("=" * 40)
    
    # Setup configuration
    setup_bot_config()
    
    # Check requirements
    all_good = check_requirements()
    
    print("\n" + "=" * 40)
    
    if all_good:
        print("✅ Setup complete!")
        print("\n📝 Next steps:")
        print("1. Edit bot_config.py and add your Discord bot token")
        print("2. Make sure src/config.py has your TikTok sessionid")
        print("3. Run: python discord_bot.py")
    else:
        print("❌ Setup incomplete - install missing packages first")

if __name__ == "__main__":
    main()
