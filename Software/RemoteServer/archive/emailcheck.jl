# load relevant
cd(joinpath(ENV["HOME"], "KilliFeeder/Software/Watchman"))
include("utils/watchman_fxns.jl") # 5.544937 seconds on macbook

# load config file
configuration = load_config("config/config") # 0.14 seconds

function mainloop(configuration)
    logged = []

    while true
        # rsync with pi server to get most updated data, NOTE: linux specific
        success = check_server_updating(configuration) # 3.222670 seconds on macbook

        # don't need this because wrapped in "continuouspull"
        time_db, feed_db, sqlite_db = pull_configure_data(configuration)

        # check whether any feeders have mysteriously fallen off the grid
        feedersDown = check_man_down(time_db, configuration)

        # check whether any feedings have been missed outside given window
        missedfeedings = check_missed_feedings(feed_db, sqlite_db, configuration)

        logged = checkAndEmail(logged, feedersDown, missedfeedings, configuration)
        # sleep for a bit
        sleep(120)
    end 
end

mainloop(configuration)

# x= time_db[1]
# y = x[x[:,4] .== "2018-11-26", :]
