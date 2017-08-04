use strict;
use warnings;
use Data::Dumper;

die "Num of args ".scalar(@ARGV) . "Usage: perl tfidf.pl is_train file idf_file tf idf norm\n" if (@ARGV != 6);
my $is_train = $ARGV[0];
my $input_file = $ARGV[1];
my $idf_file = $ARGV[2];

my $use_tf = $ARGV[3];
my $use_idf = $ARGV[4];
my $norm = $ARGV[5];

#my $input_train_file = "../data/WordNet/index/text";
#my $input_test_file = "../data/OntoNotes/index/text";

#my $use_tf = ".tf";
#my $use_idf = "";
#my $norm = "";
my $output_file = $input_file;

if ($use_tf == 1) {
    $output_file .= ".tf";
}
if ($use_idf == 1) {
    $output_file .= ".idf";
}
if ($norm == 1) {
    $output_file .= ".norm";
}

### 1. read data
my $data = &read_data($input_file);


### 2. use tf
if ($use_tf == 1) {
    print "using tf\n";
} else {
    print "no tf, all features are 1\n";
    &no_tf($data);
}

### 3. use idf
if ($use_idf == 1) {
    print "use idf: log(num_docs/(df+1))\n";
    &idf($is_train, $data, $idf_file);
} else {
    print "no idf\n";
}

### 4. normalize as unit vectors
if ($norm == 1) {
    print "use norm: unit vectors\n";
    &norm($data);
} else {
    print "no norm\n";
}

### 5. write data (features are ranked in ascending order)
&write_data($data, $output_file);


sub read_data() {
    my ($input_file) = @_;
    open(I, $input_file) || die "Cannot open $input_file\n";
    my @data;
    my $i = 0;
    while (my $str = <I>) {
	$i++;
	$str =~ s/\s+$//;
	my @words = split(/\s+/, $str);
	my %hash;
	foreach my $w (@words) {
	    $hash{$w}++;
	}
	if ($i == 1) {
	    #print "read_data: ". Dumper(%hash);
	}
	push(@data, \%hash);
    }
    close(I);
    return \@data;
}


sub write_data() {
    my ($data, $output_file) = @_;
    open(O, ">$output_file") || die "Cannot open $output_file\n";
    foreach my $doc_hash (@$data) {
	my @words = sort {$a <=> $b} keys %$doc_hash;
	foreach my $w (@words) {
	    print O "$w $doc_hash->{$w} ";
	}
	print O "\n";
    }
    close(O);
}


sub no_tf() {
    my ($data) = @_;
    for (my $i = 0; $i < @$data; $i++) {
	my $doc_hash = $data->[$i];
	foreach my $k (keys %$doc_hash) {
	    $doc_hash->{$k} = 1;
	}
    }
}


sub idf() {
    my ($is_train, $data, $idf_file) = @_;
    # 1. get idf
    my $idf = {};
    if ($is_train == 1) {
	# 1.1 if data is train data. compute doc freq
	foreach my $doc_hash (@$data) {
	    foreach my $term (keys %$doc_hash) {
		$idf->{$term}++;
	    }
	}
	my $num_docs = @$data;
	# 1.2 compute inverse doc freq
	foreach my $term (keys %$idf) {
	    $idf->{$term} = log($num_docs / ($idf->{$term}+1));
	}
	# 1.3 write idf value into $idf_file
	open(O, ">$idf_file") || die "Cannot create $idf_file\n";
	foreach my $term (sort {$a <=> $b} keys %$idf) {
	    print O "$term $idf->{$term}\n";
	}
	close(O);
    } else {
	# 1.4 if data is test data, read idf value from idf_file
	open(I, $idf_file) || die "Cannot open $idf_file\n";
	while (my $str = <I>) {
	    $str =~ s/\s+$//;
	    my ($term, $value) = split(/\s+/, $str);
	    $idf->{$term} = $value;
	}
	close(I);
    }
    my $i = 0;
    foreach my $doc_hash (@$data) {
	$i++;
	foreach my $term (keys %$doc_hash) {
	    if (!exists $idf->{$term}) {
		die "$term does not exist!\n";
	    }
	    #print "$num_docs $df->{$term} $idf\n";
	    #die;
	    $doc_hash->{$term} *= $idf->{$term};
	}
    }
}

sub norm() {
    my ($data) = @_;
    foreach my $doc_hash (@$data) {
	my $total = 0;
	foreach my $t (keys %$doc_hash) {
	    $total += $doc_hash->{$t} * $doc_hash->{$t};
	}
	$total = sqrt($total);
	##############
	$total /= 20;
	foreach my $t (keys %$doc_hash) {
	    $doc_hash->{$t} /= $total;
	}
    }
}
