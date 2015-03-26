없음 = null;
____debug = false;
____range = function(s, e) {
	var ret = [];
	for(var i = s; i < e; i ++) {
		ret.push(i);
	}
	return ret;
};
____eval = eval;

function ____slice(array, from, to, step) {
    if (from===null) from=0;
    if (to===null) to=array.length;
    if (!step) return array.slice(from, to);
    var result = Array.prototype.slice.call(array, from, to);
    if (step < 0) result.reverse();
    step = Math.abs(step);
    if (step > 1) {
        var final = [];
        for (var i = result.length - 1; i >= 0; i--) {
            (i % step === 0) && final.push(result[i]);
        };
        final.reverse();
        result = final;
   }
   return result;
}


function ____subscript(l, x) {
	if (Array.isArray(x)) {
		var ret = [];
		for(var i = 0; i < x.length; i ++)
			ret.push(l[x[i]-1]);
		return ret;
	}
    else {
        if (x > 0)
            x -= 1;
        return l[x];
	}
}

function ____print_one(x) {
    console.log(x);
}

function ____find_and_call_function(matcher, scope, functions) {
    var has_variable = function (x) {
		try {
			eval(x);
		}
		catch(e) {
			return false;
		};
		return true;
	};

    var get_variable_value = function (x) {
		return eval(x);
	};

    var try_match = function (matcher, proto) {
        if (matcher.length == 0 && proto.length == 0)
			return [[]];
        if (matcher.length == 0)
            return [];
        if (proto.length == 0)
            return [];
        if (matcher[0][0] == 'EXPR') {
            if (proto[0][0] == 'IDENTIFIER') {
                var skip = 1;
                if (proto.length >= 2 && proto[1][0] == 'WS')
                    skip = 2;
				var ret = try_match(____slice(matcher,1,null,null), ____slice(proto,skip,null,null));
				for(var i=0; i < ret.length; i ++) {
					ret[i] = [matcher[0][1]].concat(ret[i]);
				}
				return ret;
			}
			return [];
		} else { // matcher[0][0] == 'NAME'
            if (proto[0][0] == 'IDENTIFIER') {
                var sole_variable_exists = false;
				var to_ret = [];
                // 전체 이름에 해당하는 변수가 존재
                if (has_variable(matcher[0][1])) {
                    sole_variable_exists = true;
                    var skip = 1;
                    if (proto.length >= 2 && proto[1][0] == 'WS')
                        skip = 2;
					var ret = try_match(____slice(matcher,1,null,null), ____slice(proto,skip,null,null));
					for(var i = 0; i < ret.length; i ++) {
						to_ret.push([get_variable_value(matcher[0][1])].concat(ret[i]));
					}
				}

                // 정의에 빈칸 없는 경우, 잘라서 시도해본다
                if (proto.length >= 2 && proto[1][0] != 'WS') {
                    var try_sliced_str_match = function (each_str) {
						var to_ret = [];
                        if (matcher[0][1].endsWith(each_str)) {
                            var variable_name = matcher[0][1].substr(0, matcher[0][1].length-each_str.length);
                            if (has_variable(variable_name)) {
                                var skip = 2;
                                if (proto.length >= 3 && proto[2][0] == 'WS')
                                    skip = 3;
								var ret = try_match(____slice(matcher,1,null,null), ____slice(proto,skip,null,null));
								for(var i = 0; i < ret.length; i ++) {
									var sub_candidate = ret[i];
                                    if (sole_variable_exists)
                                        throw "헷갈릴 수 있는 변수명이 사용됨: " + matcher[0][1] + " / " + variable_name + "+" + each_str;
									to_ret.push([get_variable_value(variable_name)].concat(sub_candidate));
								}
							}
						}
						return to_ret;
					};
                    if (proto[1][0] == 'STRS') {
						for(var i = 0; i < proto[1][1].length; i ++) {
							var each_str = proto[1][1][i];
                            to_ret.concat(try_sliced_str_match(each_str));
						}
					} else if (proto[1][0] == 'STR') {
						to_ret.concat(try_sliced_str_match(proto[1][1]));
					}
				}
				return to_ret;
			} else if (proto[0][0] == 'STR') {
                if (matcher[0][1] == proto[0][1]) {
                    var skip = 1;
                    if (proto.length >= 2 && proto[1][0] == 'WS')
                        skip = 2;
					return try_match(____slice(matcher, 1), ____slice(proto, skip));
				}
				return [];
			} else if (proto[0][0] == 'STRS') {
				var to_ret = [];
				for(var i = 0; i < proto[0][1].length; i ++) {
					var each_str = proto[0][1][i];
                    if (matcher[0][1] == each_str) {
                        var skip = 1;
                        if (proto.length >= 2 && proto[1][0] == 'WS')
                            skip = 2;
						to_ret.concat(try_match(____slice(matcher, 1), ____slice(proto, skip)));
					}
				}
				return to_ret;
			}
		}
	};

    var candidates = [];
	for(var i = 0; i < functions.length; i ++) {
		var func = functions[i][0];
		var proto = functions[i][1];
		var ret = try_match(matcher, proto);
		for(var j = 0; j < ret.length; j ++) {
            candidates.push([func, ret[j]])
		}
	}

    if (candidates.length == 0)
        throw "해당하는 약속을 찾을 수 없습니다.";
    if (candidates.length >= 2)
        throw "적용할 수 있는 약속이 여러개입니다.";

    func = candidates[0][0];
	args = candidates[0][1];
    return func.apply(null, args);
}


____functions = [[____print_one, [['IDENTIFIER', '값'], ['WS',' '], ['STR', '보여주기']]]];
