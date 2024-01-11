from globalVars import *
from getTrack import *
import car
from sim import *
import neat


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def main(debug=False):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "./neat_config.txt",
    )
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    set_debug_flag(debug)

    pop.run(run_sim, 1000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procedural racetrack generator")
    parser.add_argument(
        "--debug",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Show racetrack generation steps",
    )
    args = parser.parse_args()
    main(debug=args.debug)
