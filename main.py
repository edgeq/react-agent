from agent.loop import run_agent_loop
import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] != "":
        user_prompt = sys.argv[1]
    else:
        user_prompt = "Say hello in a formal 1890s manner. Treat me as if you were a vendor at the 1893 World's Fair in Chicago"
    print(run_agent_loop(user_prompt))

if __name__ == "__main__":
    main()