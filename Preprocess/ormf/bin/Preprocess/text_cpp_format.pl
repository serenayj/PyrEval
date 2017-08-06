#---------------------------------------------------
# change current format into c++ read_data() format
#---------------------------------------------------

use strict;
use warnings;

die "Usage: perl text_cpp_format.pl input_file output_file\n" if (@ARGV < 2);
my $input_file = $ARGV[0];
my $output_file = $ARGV[1];
my $num_words;
$num_words = $ARGV[2] if (defined $ARGV[2]);

&cpp_format($input_file, $output_file, $num_words);

sub cpp_format() {
    my ($input_file, $output_file, $num_words) = @_;

    my $max_word = 0;
    open(I, $input_file) || die "Cannot open $input_file\n";
    my @docs;
    while (my $str = <I>) {
	$str =~ s/^\s+//;
	$str =~ s/\s+$//;
	my @data = split(/\s+/, $str);
	if (!defined $num_words) { ### if num_words is not given, then it is train data. compute the number of words
	    for (my $i = 0; $i < @data; $i=$i+2) {
		$max_word = $data[$i] if ($max_word < $data[$i]);
	    }
	}
	my $doc = scalar(@data) / 2;
	$doc .= " $str";
	push(@docs, $doc);
    }
    close(I);
    
    if (!defined $num_words) {
	$num_words = $max_word + 1;
    }
    
    open(O, ">$output_file") || die "Cannot open $output_file\n";
    print O scalar(@docs) . " $num_words\n";
    foreach my $str (@docs) {
	print O "$str\n";
    }
    close(O);

    return $num_words;
}
