<?php

if( isset( $_POST[ 'Submit' ]  ) ) {
	// Get input from POST only (not $_REQUEST)
	$target = $_POST[ 'ip' ] ?? '';
	$html = '';

	// Validate input as IP address or hostname
	$isValid = false;
	if( filter_var( $target, FILTER_VALIDATE_IP ) ) {
		$isValid = true;
	}
	elseif( filter_var( $target, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME ) ) {
		$isValid = true;
	}

	if( $isValid ) {
		// Escape shell argument to prevent command injection
		$target = escapeshellarg( $target );

		// Determine OS and execute the ping command.
		if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
			// Windows
			$cmd = shell_exec( 'ping  ' . $target );
		}
		else {
			// *nix
			$cmd = shell_exec( 'ping  -c 4 ' . $target );
		}

		// Feedback for the end user - escape output for HTML
		$html = "<pre>" . htmlspecialchars( $cmd, ENT_QUOTES, 'UTF-8' ) . "</pre>";
	}
	else {
		$html = "<pre>Error: Invalid IP address or hostname</pre>";
	}
}

?>
