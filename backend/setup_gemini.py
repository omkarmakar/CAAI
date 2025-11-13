"""
Quick setup script for CAAI Gemini Integration
Helps configure the Gemini API key for all AI-powered agents
"""
import os
from pathlib import Path

def setup_gemini_key():
    """Interactive setup for Gemini API key"""
    print("="*80)
    print(" CAAI - Gemini AI Integration Setup ".center(80))
    print("="*80)
    print()
    
    # Check if .env exists
    env_path = Path(__file__).parent / ".env"
    
    # Read existing .env if present
    existing_key = None
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    existing_key = line.split('=', 1)[1].strip().strip('"\'')
                    break
    
    if existing_key:
        print(f"✓ Existing Gemini API Key found: {existing_key[:20]}...")
        print()
        response = input("Do you want to update it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled. Existing key will be used.")
            return
    
    print()
    print("Please enter your Gemini API Key.")
    print("Get your key from: https://makersuite.google.com/app/apikey")
    print()
    
    api_key = input("Gemini API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    # Validate key format (basic check)
    if len(api_key) < 30:
        print("⚠️  Warning: API key seems too short. Please verify.")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Write to .env file
    try:
        # Read all existing lines
        lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        # Update or add GEMINI_API_KEY
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith('GEMINI_API_KEY='):
                lines[i] = f'GEMINI_API_KEY={api_key}\n'
                key_found = True
                break
        
        if not key_found:
            lines.append(f'GEMINI_API_KEY={api_key}\n')
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        print()
        print("="*80)
        print("✅ Success! Gemini API Key configured.")
        print("="*80)
        print()
        print("Next steps:")
        print("1. Run tests: python test_gemini_agents.py")
        print("2. Start backend: python main.py")
        print("3. Test agents via API at http://localhost:8000")
        print()
        print("📖 For detailed documentation, see: GEMINI_INTEGRATION_GUIDE.md")
        print()
        
    except Exception as e:
        print(f"❌ Error writing to .env file: {str(e)}")
        print()
        print("Manual setup: Create/edit backend/.env file and add:")
        print(f"GEMINI_API_KEY={api_key}")

def verify_setup():
    """Verify the setup is correct"""
    print()
    print("Verifying setup...")
    print()
    
    try:
        import config
        if config.GEMINI_API_KEY:
            print(f"✓ GEMINI_API_KEY loaded: {config.GEMINI_API_KEY[:20]}...")
            print("✓ Configuration is valid!")
            return True
        else:
            print("❌ GEMINI_API_KEY not loaded from config")
            return False
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        return False

def main():
    """Main setup function"""
    setup_gemini_key()
    
    # Verify
    print()
    response = input("Verify configuration now? (Y/n): ").strip().lower()
    if response != 'n':
        verify_setup()
    
    print()
    print("Setup complete! 🎉")
    print()

if __name__ == "__main__":
    main()
