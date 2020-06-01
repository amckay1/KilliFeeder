function pulldb()
    dbfile = joinpath(ENV["HOME"], ".KilliFeeder/data/db.sqlite")
	while true
		run(`/usr/bin/rsync -avze "ssh -i /home/pi/.ssh/killifeeder.pem" ubuntu@www.KilliFeeder.com:/home/ubuntu/.KilliFeeder/data/db.sqlite $dbfile`)
		sleep(3)
	end
end

pulldb()
