<?php
// Round-trip Divi 5 block files through WordPress/Divi's parser and WP's serializer.
//   wp eval-file roundtrip.php FILE... [out=DIR]
// For each file: parse_blocks() (Divi's BlockParser is the registered block_parser_class)
// -> serialize_blocks(); prints whether the result is byte-identical, the first difference,
// and any block whose JSON failed to decode (attrs === [] while the comment carried JSON).
$out_dir = null;
$files   = [];
foreach ( $args as $a ) {
	if ( 0 === strpos( $a, 'out=' ) ) {
		$out_dir = substr( $a, 4 );
	} else {
		$files[] = $a;
	}
}

function d5rt_walk( array $blocks, callable $fn ) {
	foreach ( $blocks as $b ) {
		$fn( $b );
		if ( ! empty( $b['innerBlocks'] ) ) {
			d5rt_walk( $b['innerBlocks'], $fn );
		}
	}
}

foreach ( $files as $f ) {
	$in     = file_get_contents( $f );
	$blocks = parse_blocks( $in );
	$out    = serialize_blocks( $blocks );
	$n      = 0;
	$bad    = 0;
	d5rt_walk(
		$blocks,
		function ( $b ) use ( &$n, &$bad ) {
			if ( null === $b['blockName'] ) {
				return;
			}
			++$n;
			if ( empty( $b['attrs'] ) && 'divi/placeholder' !== $b['blockName'] ) {
				++$bad;
			}
		}
	);
	$name = basename( $f );
	// Semantic check: same block tree (names + decoded attrs) after re-parsing the output,
	// and the serializer output is a fixed point (serialize(parse(out)) === out).
	$shape = function ( $bs ) use ( &$shape ) {
		$r = [];
		foreach ( $bs as $b ) {
			if ( null === $b['blockName'] ) {
				continue;
			}
			$r[] = [ $b['blockName'], $b['attrs'], $shape( $b['innerBlocks'] ) ];
		}
		return $r;
	};
	$blocks2  = parse_blocks( $out );
	$same     = $shape( $blocks ) === $shape( $blocks2 ) ? 'same-tree' : 'TREE-CHANGED';
	$fixed    = serialize_blocks( $blocks2 ) === $out ? 'fixed-point' : 'NOT-FIXED';
	$name    .= " [$same, $fixed]";
	if ( $out === $in ) {
		WP_CLI::log( sprintf( '%-70s IDENTICAL  blocks=%d empty-attrs=%d', $name, $n, $bad ) );
	} else {
		$i = 0;
		$l = min( strlen( $in ), strlen( $out ) );
		while ( $i < $l && $in[ $i ] === $out[ $i ] ) {
			++$i;
		}
		WP_CLI::log( sprintf( '%-70s DIFFERS    blocks=%d empty-attrs=%d len %d -> %d, first diff @%d', $name, $n, $bad, strlen( $in ), strlen( $out ), $i ) );
		WP_CLI::log( '    in : ' . substr( $in, max( 0, $i - 40 ), 120 ) );
		WP_CLI::log( '    out: ' . substr( $out, max( 0, $i - 40 ), 120 ) );
	}
	if ( $out_dir ) {
		file_put_contents( rtrim( $out_dir, '/' ) . '/' . basename( $f ), $out );
	}
}
