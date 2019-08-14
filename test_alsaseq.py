import alsaseq

alsaseq.client( 'EMPIMIDI', 1, 1, False )

while 1:
	if alsaseq.inputpending():
		ev = alsaseq.input()
		alsaseq.output(ev)
