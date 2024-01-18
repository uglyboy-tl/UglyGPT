Makefile = """.PHONY: install uninstall

install:
	@echo "Installing {name} service and application..."
	install -d {path}
    rsync -av --exclude='Makefile' --exclude='*.service' ./ {path}/
	install -m 644 {service_name}.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl enable {service_name}
	systemctl start {service_name}

uninstall:
	@echo "Uninstalling {name} service and application..."
	systemctl stop {service_name}
	systemctl disable {service_name}
	rm /etc/systemd/system/{service_name}.service
	rm -r {path}
	systemctl daemon-reload
"""

Service = """[Unit]
Description=FastAPI web application
After=network.target

[Service]
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000
WorkingDirectory={path}
User=www-data
Group=www-data
Restart=always

[Install]
WantedBy=multi-user.target
"""