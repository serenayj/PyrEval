#---------------------------------------------------------
# delete the word that contains a non-word character
#---------------------------------------------------------

use strict;
use warnings;

die "perl clean.pl input_file output_file\n" if (@ARGV != 2);

my $input_file = $ARGV[0];
my $output_file = $ARGV[1];

open(I, $input_file) || die "Cannot open $input_file\n";
open(O, ">$output_file") || die "Cannot create $output_file\n";

while (my $str = <I>) {
    $str =~ s/\s+$//;
    foreach my $token (split(/\s+/, $str)) {
	next if ($token =~ /\W/);
	print O "$token ";
    }
    print O "\n";
}

close(I);
close(O);
