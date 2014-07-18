all: addons

design/infrastructure.xmi: design/infrastructure.zargo
	-echo "REBUILD infrastructure.xmi from infrastructure.zargo. I cant do it"

addons: infrastructure

infrastructure: design/infrastructure.uml
	xmi2oerp -r -i $< -t addons -v 2

clean:
	rm -rf addons/infrastructure/*
	sleep 1
	touch design/infrastructure.uml
