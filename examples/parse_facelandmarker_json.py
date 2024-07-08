import argparse
import json
import plotext as plt


def parse_file(filename):
    """
  Parses an ND JSON file for the face landmarker plots one value

  Args:
    filename: The name of the file to parse.
  """
    try:
        x_series = []
        y_series = []
        t_series = []
        start_t = None
        with open(filename, 'r') as f:
            for line in f:
                try:
                    # Parse the line as JSON
                    data = json.loads(line.strip())
                    if len(data['faceLandmarks']) < 1:
                        continue

                    try:
                        x = data['faceLandmarks'][0]['x']
                        y = data['faceLandmarks'][0]['y']
                        t = data['timeStamp']
                        x_series.append(x)
                        y_series.append(y)
                        if start_t is None:
                            start_t = t
                        t_series.append((t - start_t) / 1000.0)
                    except IndexError:
                        print(data)
                except json.JSONDecodeError:
                    print(f"Error: Line '{line.strip()}' is not valid JSON.")

        plt.plot(t_series, x_series, label="plot")
        plt.title("Multiple Data Set")
        plt.show()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a file")
    parser.add_argument("filename", type=str, help="The name of the file to parse")
    args = parser.parse_args()

    parse_file(args.filename)
