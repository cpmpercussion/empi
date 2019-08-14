import alsaseq
# http://pp.com.mx/python/alsaseq/project.html
alsaseq.client('EMPIMIDI', 1, 1, False)

alsaseq.connectfrom(1, 128, 0)
alsaseq.connectto(0, 128, 0)

while 1:
	if alsaseq.inputpending():
		ev = alsaseq.input()
		alsaseq.output(ev)
