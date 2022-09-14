import sys, csv,os
import collect_tweets
import collect_reddits
import collect_stackoverflow
import json
import argparse
import combine_dataframes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--task", type=str, required=True, 
        choices=["collect-tweet", "clean-csv-dfs", "merge-dfs", "collect-reddit","collect-stackoverflow"], 
        help='what do you want to do?')
    parser.add_argument("--out_dir", required=True, type=str, 
        default='', help='out put directory')
    parser.add_argument( "--in_dir", type=str, default='',
        help="input directory")
    parser.add_argument( "--kw_file", type=str, 
        help="files containig search keywords/hashtags/...")
    parser.add_argument( "--stat_dir", type=str, 
        default='', help="tweet stat dir")
    
    args = parser.parse_args()
    return args



if __name__ == "__main__":
    print("Hello, Welcome to SMSA Toolkit. What can I do for you?")
    menu = """
                                                                
      _______   __     __       ____        _______    __________   
     / ______| |  \\  /  |      /    \\      / _____|   /  /   /  /|
     |  \___   |   \\/   |     /  /\  \\     | \___    /_ /___/ _/ | 
      \____ \\  |        |    /  /__\\  \\     \____ \\  |         | |
      _____| | | |\\  /| |   /  ______  \\   _____| |  |         | |
     |______/  |_| \\/ |_|  /__/      \\__\\  |______/  |_________|/
                                 
                                              
        """
    print(menu)
    print('=========================================================================')
    print('                        Welcome to SMSA Toolkit')
    print('=========================================================================')
    print('                 Use -h to list possible arguments')
    args = parse_args()

    if  args.task=='merge-dfs':
        combine_dataframes.merge_dfs(indir=args.in_dir, outdir=args.out_dir)
    elif args.task=='clean-csv-dfs':
        combine_dataframes.clean_csv_dfs(indir=args.in_dir, 
            outdir=args.out_dir, tag_file=args.kw_file, stat_dir=args.stat_dir)
    elif args.task=='collect-tweet':
        collect_tweets.collect_tweets(args.out_dir, args.kw_file, args.stat_dir)
    elif args.task=='collect-reddit':
        collect_reddits.collect_reddits(args.out_dir, args.kw_file)
    elif args.task=='collect-stackoverflow':
        collect_stackoverflow.collect_stack(args.out_dir, args.kw_file)

