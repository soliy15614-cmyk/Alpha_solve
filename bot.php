<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";
$waryono = "cookies.txt";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";
const bg_hitam  = "\033[40m";
const bg_merah  = "\033[41m";
const bg_hijau  = "\033[42m";
const bg_kuning = "\033[43m";
const bg_biru   = "\033[44m";
const bg_ungu   = "\033[45m";
const bg_cyan   = "\033[46m";
const bg_putih  = "\033[47m";

const version     = "1.0";
const script_name = "makeyoutask.com";
const host        = "https://makeyoutask.com";
const in      = "https://api.waryono.my.id/in.php";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = []) {
    while (true) {
        $ch = curl_init();
        $final_headers = [];
        foreach ($headers as $header) {
            $final_headers[] = $header;
        }
        $options = [
            CURLOPT_URL            => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HEADER         => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYHOST => 1,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER     => $final_headers,
            CURLOPT_CONNECTTIMEOUT => 999,
            CURLOPT_TIMEOUT        => 999,
            CURLOPT_COOKIEFILE => 'cookies.txt',
            CURLOPT_COOKIEJAR => 'cookies.txt'
        ];
        if (strtoupper($method) === 'POST') {
            $options[CURLOPT_POST] = true;
            $options[CURLOPT_POSTFIELDS] = $data;
        }
        curl_setopt_array($ch, $options);
        $response = curl_exec($ch);
        if ($response) {
            $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
            $body = substr($response, $header_size);
            curl_close($ch);
            return $body;
        } else {
            curl_close($ch);
            echo "\33[1;" . rand(30, 37) . "mwiwok detok";
            sleep(1);
            echo "\r \r";
            return "ngelek";
        }
    }
}

function timer($seconds, $prefix = "[!] please wait") {
    $wait_time = (int)$seconds;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $frame_count = count($frames);
    $current_frame = 0;
    $frame_delay = 0.1;
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $hours = floor($wait_time / 3600);
            $minutes = floor(($wait_time % 3600) / 60);
            $seconds_left = $wait_time % 60;
            $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
            $spinner = $frames[$current_frame];
            echo putih . $prefix . hijau . " $time_formatted " . putih . $spinner . "\r";
            usleep($frame_delay * 1000000);
            $current_frame = ($current_frame + 1) % $frame_count;
            if ((microtime(true) - $start_time) >= 1) {
                break;
            }
        }
        $wait_time--;
    }
    echo "\r                                     \r";
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "API Key   : " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Email     : " . kuning;
        $email = trim(fgets(STDIN));
        echo putih . "Password  : " . kuning;
        $password = trim(fgets(STDIN));
        $data = [
            "apikey"   => $apikey,
            "email"    => $email,
            "password" => $password
        ];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "Konfigurasi disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

function cloud($apikey, $sitekey, $cdata = '') {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey"  => $apikey,
        "methods" => "turnstile",
        "domain"  => host,
        "sitekey" => $sitekey,
        "action"  => "submit",
        "cdata"   => $cdata,
        "json"    => 1
    ]);
    $request = skibidixxx(in, "POST", $body, $headers);
    if (strpos($request, "ERROR_WRONG_METHOD") !== false)              { echo putih."Error: ".merah."ERROR_WRONG_METHOD\n"; exit; }
    if (strpos($request, "ERROR_KEY_DOES_NOT_EXIST") !== false)        { echo putih."Error: ".merah."ERROR_KEY_DOES_NOT_EXIST\n"; exit; }
    if (strpos($request, "ERROR_METHOD_NOT_SPECIFIED") !== false)      { echo putih."Error: ".merah."ERROR_METHOD_NOT_SPECIFIED\n"; exit; }
    if (strpos($request, "ERROR_NO_SUCH_METHOD") !== false)            { echo putih."Error: ".merah."ERROR_NO_SUCH_METHOD\n"; exit; }
    if (strpos($request, "ERROR_DATABASE_CONNECTION_FAILED") !== false){ echo putih."Error: ".merah."ERROR_DATABASE_CONNECTION_FAILED\n"; exit; }
    if (strpos($request, "ERROR_TOO_MANY_REQUESTS") !== false) {
        echo putih."Error: ".merah."ERROR_TOO_MANY_REQUESTS";
        sleep(1.8); echo "\r                                               \r";
        return "ERROR_TOO_MANY_REQUESTS";
    }
    if (strpos($request, "ERROR_WRONG_USER_KEY") !== false)  { echo putih."Error: ".merah."ERROR_WRONG_USER_KEY\n"; exit; }
    if (strpos($request, "ERROR_ZERO_BALANCE") !== false)    { echo putih."Error: ".merah."ERROR_ZERO_BALANCE\n"; exit; }
    if (strpos($request, "ERROR_BAD_PARAMETERS") !== false)  { echo putih."Error: ".merah."ERROR_BAD_PARAMETERS\n"; exit; }
    if (strpos($request, "ERROR_EMPTY_IMAGE") !== false)     { echo putih."Error: ".merah."ERROR_EMPTY_IMAGE\n"; exit; }
    if (strpos($request, "ERROR_UNKNOWN") !== false)         { echo putih."Error: ".merah."ERROR_UNKNOWN\n"; exit; }

    $json = json_decode($request, true);
    $id   = $json["request"];

    reload:
    timer(3, "  cf");
    $url    = "https://api.waryono.my.id/res.php?apikey=".$apikey."&id=".$id."&json=1";
    $result = skibidixxx($url, "GET", []);

    if (strpos($result, "ERROR_BAD_PARAMETERS") !== false)        { echo putih."Error: ".merah."ERROR_BAD_PARAMETERS\n"; exit; }
    if (strpos($result, "Database connection failed") !== false)   { echo putih."Error: ".merah."Database connection failed\n"; exit; }
    if (strpos($result, "WRONG_CAPTCHA_ID") !== false) {
        echo putih."Error: ".merah."WRONG_CAPTCHA_ID";
        sleep(1.8); echo "\r                                               \r";
        return "WRONG_CAPTCHA_ID";
    }
    if (strpos($result, "ERROR_SOLVE_PENDING") !== false) {
        echo putih."Error: ".merah."ERROR_SOLVE_PENDING";
        sleep(1.8); echo "\r                                               \r";
        return "ERROR_SOLVE_PENDING";
    }
    if (strpos($result, "CAPCHA_NOT_READY") !== false) {
        echo putih."Error: ".merah."CAPCHA_NOT_READY";
        sleep(1.8); echo "\r                                               \r";
        goto reload;
    }
    if (strpos($result, "ERROR_CAPTCHA_UNSOLVABLE") !== false) {
        echo putih."Error: ".merah."ERROR_CAPTCHA_UNSOLVABLE";
        sleep(1.8); echo "\r                                               \r";
        return "ERROR_CAPTCHA_UNSOLVABLE";
    }
    if (strpos($result, "ERROR_BAD_REQUEST") !== false)    { echo "Error: ".merah."ERROR_BAD_REQUEST\n"; exit; }
    if (strpos($result, "INTENAL_SERVER_ERROR") !== false) {
        echo "Errro: ".merah."INTENAL_SERVER_ERROR";
        sleep(1.8); echo "\r                                               \r";
        return "INTENAL_SERVER_ERROR";
    }

    $json = json_decode($result, true);
    $res  = $json["request"];
    return ["turnstile" => $res];
}

function allsuki(&$a,&$b,&$c){
	$a = [
		'host: '.script_name,
		'sec-ch-ua-platform: "Android"',
		'save-data: on',
		'upgrade-insecure-requests: 1',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36',
		'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7',
		'sec-fetch-site: none',
		'sec-fetch-mode: navigate',
		'sec-fetch-user: ?1',
		'sec-fetch-dest: document',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
	$b = [
		'host: '.script_name,
		'sec-ch-ua-platform: "Android"',
		'save-data: on',
		'origin: '.host,
		'content-type: application/x-www-form-urlencoded',
		'upgrade-insecure-requests: 1',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36',
		'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7',
		'sec-fetch-site: same-origin',
		'sec-fetch-mode: navigate',
		'sec-fetch-user: ?1',
		'sec-fetch-dest: document',
		'referer: '.host.'/login',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
	$c = [
		'host: makeyoutask.com',
		'sec-ch-ua-platform: "Android"',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36',
		'origin: '.host,
		'sec-fetch-site: same-origin',
		'sec-fetch-mode: cors',
		'sec-fetch-dest: empty',
		'referer: '.host.'/youtubeviews',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
}
home:
clear();
$config   = getConfig($configFile);
$apikey   = $config['apikey'];
$email    = $config['email'];
$password = $config['password'];

clear();

allsuki($a,$b,$c);
$url = host."/dashboard";
$dash = skibidixxx($url, "GET", [], $b);
if (strpos($dash, "Dashboard | MakeYouTask.Com") !== false){
	preg_match('/Welcome, <span>([^<]+)<\/span>/', $dash, $user);
	$username = $user[1] ?? 'Guest';
	preg_match('/class="level">([^<]+)<\/span>/', $dash, $lvl);
	$level = $lvl[1] ?? 'Level 0';
	preg_match('/class="exp">([^<]+)<\/span>/', $dash, $exp);
	$current_exp = $exp[1] ?? '0/0';
	preg_match('/<h2>([^<]+)<\/h2>\s*<p>Main Balance/', $dash, $bal);
	$balance = $bal[1] ?? '0 Token';
	echo putih."user: ".cyan.$username.putih." balance: ".biru.$balance."\n";
	echo putih."level: ".biru.$level.putih." (".biru.$current_exp.putih.")\n";


	reload:
	echo "\n";
	echo putih."[mission:".kuning." youtubeviews".putih."]\n";
	echo putih."------------------------------------------\n";
	$url = host."/youtubeviews/checkDevice";
	$checkDevice = skibidixxx($url, "GET", [], $a);
	if (preg_match('/<h2 class="yv-title">Device Supported!<\/h2>/', $checkDevice)) {
	    echo putih."[STATUS] ".hijau."OK - Device Supported!\n";
	    goto lanjut;

	} else {
	    echo putih."[STATUS] ".merah."Not Supported\n";
	    goto ptc;
	}

	lanjut:
	$url = host."/youtubeviews";
	$youtubeviews = skibidixxx($url, "GET", [], $a);
	preg_match('/name="csrf_token_name".*?value="([^"]+)"/', $youtubeviews, $csrf);
	$token = $csrf[1] ?? '';
	preg_match('/data-sitekey="([^"]+)"/', $youtubeviews, $site);
	$sitekey = $site[1] ?? '';
	preg_match('/let timer = (\d+);/', $youtubeviews, $tmr);
	preg_match('/let adId = (\d+);/', $youtubeviews, $id);
	$waktu = $tmr[1] ?? 0;
	$ad_id = $id[1] ?? '';
	if ($ad_id) {
		$url = host."/youtubeviews/start_session";
		$data = [
			'ad_id' => $ad_id,
			'timer' => $waktu,
			'csrf_token_name' => $token
		];
	$start_session = skibidixxx($url, "POST", $data, $c);
	preg_match('/"status":"success"/', $start_session, $check);
	preg_match('/"csrf_hash":"([^"]+)"/', $start_session, $res);
	$csrf_hash = $res[1] ?? '';
	if ($check && $csrf_hash) {
	    timer($waktu, "  watching...");
	    sleep(2);
	    $url = host."/youtubeviews/verify";
	    if (empty($sitekey)) {
	        $data = http_build_query([
	            "csrf_token_name" => $csrf_hash
	        ]);
	        $claim = skibidixxx($url, "POST", $data, $b);
	        if (preg_match('/Notiflix\.Notify\.success\("([^"]+)"\);/', $claim, $msg)) {
	            echo putih."[INFO] " . hijau . $msg[1] . "\n";
	            goto lanjut;
	        } else {
	            echo putih."[INFO] " . merah . "Error Invalid Claim\n";
	            goto lanjut;
	        }
	    }
	    tryy:
	    $bypass = cloud($apikey, $sitekey);
	    if (is_array($bypass)) {
	    $data = http_build_query([
	    	  "csrf_token_name" => $csrf_hash,
	    	  "captcha" => "turnstile",
	    	  "cf-turnstile-response" => $bypass["turnstile"]
	    ]);
	    $claim = skibidixxx($url, "POST", $data, $b);
	    if (preg_match('/Notiflix\.Notify\.success\("([^"]+)"\);/', $claim, $msg)) {
	        echo putih."[INFO] " . hijau . $msg[1] . "\n";
	        goto lanjut;

	    } else {
	        echo putih."[INFO] " . merah . "Errror Invalid Claim Or captcha\n";
	        goto lanjut;
	    }
	    
	   } elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
	     goto tryy;
	    
	 } else {
	     echo putih."Error: ".merah." Tidak di ketahui!! coba lagi...\n";
	     goto lanjut;
}

	} else {
	    echo putih."[ERROR] " . merah . "Error - task YouTubeviews\n";
	    goto ptc;
	}


	} else {
	    echo putih."[INFO] ".merah."No Task Available!\n";
	    goto ptc;
	}

	ptc:
	echo "\n";
	echo putih."[mission:".kuning." ptc windows".putih."]\n";
	echo putih."------------------------------------------\n";

	kopet:
	$url = host."/ptc";
	$ptc = skibidixxx($url, "GET", [], $a);
	preg_match_all('/wmv-url="([^"]+)"\s*wmv-sec="(\d+)"/', $ptc, $res);
	$url_view = $res[1][0] ?? '';
	$detik    = $res[2][0] ?? 0;
	if ($url_view) {
		$go = skibidixxx($url_view, "GET", [], $a);
		timer($detik, "  watching...");
		$url = host."/ptc/getCaptcha";
		$getCaptcha = skibidixxx($url, "GET", [], $a);
		preg_match('/name="csrf_token_name" value="([^"]+)"/', $getCaptcha, $csrf);
		$token = $csrf[1] ?? '';
		preg_match('/data-sitekey="([^"]+)"/', $getCaptcha, $site);
		$sitekey = $site[1] ?? '';

		tai:
		$bypass = cloud($apikey, $sitekey);
		if (is_array($bypass)) {
		$url = host."/ptc/verifyWindow";
		$data = http_build_query([
			  "csrf_token_name" => $token,
			  "captcha" => "turnstile",
			  "cf-turnstile-response" => $bypass["turnstile"]
		]);
		$claim = skibidixxx($url, "POST", $data, $b);
		if (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/", $claim, $msg)) {
		    echo putih."[INFO] " . hijau . $msg[1] . "\n";
		    goto kopet;
		    
		} else {
		    echo putih."[INFO] " . merah . "Error captcha or expired task\n";
		    goto kopet;
		}

	} elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
		  goto tai;
		
	} else {
	  echo putih."Error: ".merah." Tidak di ketahui!! coba lagi...\n";
	  goto kopet;
}
				
	} else {
	  echo putih."[INFO] ".merah."No Task Available!\n";
	  goto iframe;

	}	

	iframe:
	echo "\n";
	echo putih."[mission:".kuning." ptc iframe".putih."]\n";
	echo putih."------------------------------------------\n";
	coli:
	$url = host."//ptc/index/iframe";
	$iframe = skibidixxx($url, "GET", [], $a);
	preg_match_all("/window\.location\s*=\s*'([^']+)'/", $iframe, $res);
	$url_view = $res[1][0] ?? '';
	if ($url_view) {
		$xhamters = skibidixxx($url_view, "GET", [], $a);
		preg_match('/action="([^"]+ptc\/verify\/[^"]+)"/', $xhamters, $act);
		$action = $act[1] ?? '';
		preg_match('/data-sitekey="([^"]+)"/', $xhamters, $site);
		$sitekey = $site[1] ?? '';
		preg_match('/name="csrf_token_name" value="([^"]+)"/', $xhamters, $csrf);
		$token = $csrf[1] ?? '';
		preg_match('/var timer = (\d+);/', $xhamters, $tmr);
		$wait = $tmr[1] ?? 0;
		timer($wait, "  watching...");

		nyawit:
		$bypass = cloud($apikey, $sitekey);
		if (is_array($bypass)) {
			$data = http_build_query([
				  "captcha" => "turnstile",
				  "cf-turnstile-response" => $bypass["turnstile"],
				  "csrf_token_name" => $token
			]);
		$claim = skibidixxx($action, "POST", $data, $b);
		if (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/s", $claim, $msg)) {
		    $pesan = str_replace(['<br>', '<br/>', '<br />'], ' ', $msg[1]);
		    echo putih."[INFO] " . hijau . trim($pesan) . "\n";
		    goto coli;

		} else {
		    echo putih."[INFO] " . merah . "Error Task Or captcha\n";
		    goto coli;
		}
		
		} elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
			  goto nyawit;
		
    } else {
		  echo putih."Error: ".merah." Tidak di ketahui!! coba lagi...\n";
		  goto coli;
	 }
		
		
	} else {
	    echo putih."[INFO] ".merah."No Task Available!\n\n";
	    timer(300, "  waiting task please..");
	    goto reload;
	}
	
} else {
	allsuki($a,$b,$c);
	echo kuning."login required...!\n";

	ulang:
	$url = host."/login";
	$login = skibidixxx($url, "GET", [], $a);
	preg_match('/action="([^"]+auth\/login)"/', $login, $act);
	$action = $act[1] ?? '';
	preg_match('/name="csrf_token_name" value="([^"]+)"/', $login, $csrf);
	$token = $csrf[1] ?? '';
	preg_match('/data-sitekey="([^"]+)"/', $login, $site);
	$sitekey = $site[1] ?? '';
	$bypass = cloud($apikey, $sitekey);
	if (is_array($bypass)) {
	$data = http_build_query([
		  "csrf_token_name" => $token,
		  "email" => $email,
		  "password" => $password,
		  "captcha" => "turnstile",
		  "cf-turnstile-response" => $bypass["turnstile"]
	]);
	$login = skibidixxx($action, "POST", $data, $b);
	if (preg_match('/Dashboard \| MakeYouTask\.Com/i', $login)) {
	    echo putih."[INFO] ".hijau."Login Success, go -> Dashboard.\n";
	    sleep(2);
	    goto home;
	    
	} elseif (preg_match('/alert-danger">.*?<\/i>\s*([^<]+)/s', $login, $fail)) {
	    echo putih."[INFO] ".merah.trim($fail[1])."\n";
	    @unlink($waryono);
	    @unlink($configFile);
	    exit;
	} else {
	    echo putih."[INFO] ".kuning."Error tidak diketahui, mungkin Cloudflare atau IP Block!\n";
	    @unlink($waryono);
	    @unlink($configFile);
	    exit;
	}

	} elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
	  goto ulang;

    } else {
	  echo putih."Error: ".merah." Tidak di ketahui!! coba lagi...\n";
	  goto ulang;
 }

}
