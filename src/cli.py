# cli.py
import argparse
from backends.backend_memcache import MemcachedBackend
from backends.backend_singlestore import SingleStoreBackend
from service import (
    add_event,
    get_event_by_id,
    get_user_events
)
from data_generator import generate_event, generate_events_batch


def load_backend(name: str):
    if name == "memcached":
        return MemcachedBackend()
    elif name == "singlestore":
        return SingleStoreBackend()
    else:
        raise ValueError(f"Unknown backend: {name}")


def main():
    parser = argparse.ArgumentParser(description="In-memory benchmark CLI application")

    parser.add_argument(
        "--backend",
        type=str,
        choices=["memcached", "singlestore"],
        required=True,
        help="Storage backend to use",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Command: add-event ---
    add_cmd = subparsers.add_parser("add-event", help="Add an event")
    add_cmd.add_argument("--user", type=int, required=True)
    add_cmd.add_argument("--type", type=str, required=True)

    # --- Command: get-event ---
    get_cmd = subparsers.add_parser("get-event", help="Read an event by ID")
    get_cmd.add_argument("--id", type=str, required=True)

    # --- Command: user-events ---
    user_cmd = subparsers.add_parser("user-events", help="List events for a user")
    user_cmd.add_argument("--user", type=int, required=True)

    # --- Command: generate-batch ---
    batch_cmd = subparsers.add_parser("generate-batch", help="Generate a batch of events")
    batch_cmd.add_argument("--number", type=int, required=True, help="Number of events to generate")

    args = parser.parse_args()

    # Initialize backend
    backend = load_backend(args.backend)

    # Route to the selected command
    if args.command == "add-event":
        event = generate_event(
            user_id=args.user,
            event_type=args.type
        )
        add_event(backend, event)
        print("Event added:", event["event_id"])

    elif args.command == "get-event":
        evt = get_event_by_id(backend, args.id)
        print(evt)

    elif args.command == "user-events":
        events = get_user_events(backend, args.user)
        print(f"{len(events)} events found")
        for e in events:
            print(e)

    elif args.command == "generate-batch":
        events = generate_events_batch(args.number)
        for event in events:
            add_event(backend, event)
        print(f"Generated {len(events)} events")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
