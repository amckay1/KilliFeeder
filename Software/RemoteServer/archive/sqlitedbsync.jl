using CRC32c

dbfilepath = joinpath(ENV["HOME"], "KilliFeeder", "Software", "Server", "db.sqlite")
pathonrpi3 = joinpath("/home", "pi", "KilliFeeder", "Software", "Server", "db.sqlite")

function continuouslysync(dbfilepath, pathonrpi3)
    lastcheck = CRC32c.crc32c(read(dbfilepath))
    println(lastcheck)
    while true
        newcheck = CRC32c.crc32c(read(dbfilepath))
        if !(isequal(newcheck, lastcheck))
            run(`rsync -avze "ssh -i ~/.ssh/rpi3key" $dbfilepath pi@171.65.16.106:$pathonrpi3`)
            # if unable to sync, need to email warning to user
            lastcheck = newcheck
        end
        sleep(1)
    end
end

continuouslysync(dbfilepath, pathonrpi3)




