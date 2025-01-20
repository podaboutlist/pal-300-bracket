# Modified from https://stackoverflow.com/a/65418112
def find_key_nonrecursive(needle: any, haystack: dict) -> any:
	stack = [haystack]
	while stack:
		d = stack.pop()

		# python gets angry when we try to iterate over these
		if type(d) is list or type(d) is int:
			continue

		if needle in d:
			return d[needle]
		for v in d.values():
			if isinstance(v, dict):
				stack.append(v)
			if isinstance(v, list):
				stack += v

	return None
