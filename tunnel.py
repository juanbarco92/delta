from pyngrok import ngrok
import sys

def start_tunnel():
    # Helper to install ngrok binary if not present
    print("Ensuring ngrok is installed...")
    
    try:
        # Open a HTTP tunnel on port 8000
        public_url = ngrok.connect(8000).public_url
        print(f" * Tunnel established!")
        print(f" * Public URL: {public_url}")
        
        # Update .env
        env_path = ".env"
        new_lines = []
        import os
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if not line.startswith("REDIRECT_URI="):
                        new_lines.append(line)
        
        new_redirect = f"REDIRECT_URI={public_url}/auth/callback\n"
        new_lines.append(new_redirect)
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        print(f" * Updated .env with: {new_redirect.strip()}")
        print(" * Press Ctrl+C to stop the tunnel...")
        
        # Keep the process alive
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("Shutting down tunnel...")
        ngrok.kill()

if __name__ == "__main__":
    start_tunnel()
