<?php
/*
 * Shortcode [mavlab_github file="website/opensourcecode.html"]: shows an HTML file of
 * https://github.com/tudelft/publications (branch master) on a WordPress page.
 *
 * Install as a PHP snippet in WPCode (Code Snippets > Add Snippet > PHP, run everywhere).
 *
 * - only .html files in website/ of this repository
 * - the file is cached for an hour; when GitHub does not answer, the last good copy is shown
 * - HTML is filtered like post content (wp_kses_post: no scripts, no styles); the only
 *   shortcode that is expanded is teachPress [tpsingle]
 */
function mavlab_github_include( $atts ) {
	$atts = shortcode_atts( array( 'file' => '' ), $atts );
	$file = $atts['file'];
	if ( ! preg_match( '#^website/[A-Za-z0-9_-]+\.html$#', $file ) ) {
		return '<!-- mavlab_github: file not allowed -->';
	}
	$cache = 'mavlab_github_' . md5( $file );
	$body  = get_transient( $cache );
	if ( false === $body ) {
		$response = wp_remote_get( 'https://raw.githubusercontent.com/tudelft/publications/master/' . $file, array( 'timeout' => 15 ) );
		if ( ! is_wp_error( $response ) && 200 === wp_remote_retrieve_response_code( $response ) ) {
			$body = wp_remote_retrieve_body( $response );
			update_option( $cache . '_last', $body, false );
		} else {
			$body = get_option( $cache . '_last', '' );
		}
		set_transient( $cache, $body, HOUR_IN_SECONDS );
	}
	$body = wp_kses_post( $body );
	return preg_replace_callback(
		'/\[tpsingle [^\]]*\]/',
		function ( $m ) {
			return do_shortcode( $m[0] );
		},
		$body
	);
}
add_shortcode( 'mavlab_github', 'mavlab_github_include' );
