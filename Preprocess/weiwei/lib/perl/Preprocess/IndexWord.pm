use strict;
use warnings;

package Preprocess::IndexWord;
1;


sub new() {
    my ($self, $vocab_file) = @_;
    my %vocab;

    if (-e $vocab_file) {
	# if vocab_file already exists, read all the words
	open(V, $vocab_file) || die "Cannot open $vocab_file\n";
	while (my $str = <V>) {
	    $str =~ s/\s+$//;
	    my @info = split("\t", $str);
	    $vocab{$info[0]} = keys %vocab;
	}
    } else {
	# otherwise, create a new file
	open(V, ">$vocab_file") || die "Cannot create $vocab_file\n";
	print V "";
    }
    close(V);


    $self = {
	vocab => \%vocab,
	vocab_file => $vocab_file,
    };
    bless $self;
}


sub query() {
    my ($self, $word, $is_train) = @_;
    die "argument is_train is missing!\n" if (!defined $is_train);
    my $vocab = $self->{vocab};
    if (!exists $vocab->{$word}) {
	if ($is_train != 1) {
	    return -1;
	} else {
	    $vocab->{$word} = keys %$vocab;
	}
    }
    return $vocab->{$word};
}


sub voc_size() {
    my ($self) = @_;
    my $vocab = $self->{vocab};
    return keys %$vocab;
}


#---------------------
# write vocab into file
#---------------------
sub DESTROY() {
    my ($self) = @_;
    my $vocab = $self->{vocab};
    print "[Preprocess::IndexWord->DESTROY()]: vocab size = " . scalar(keys %$vocab) . "\n";
    my $vocab_file = $self->{vocab_file};
    open(V, ">$vocab_file") || die "Cannot create $vocab_file\n";
    my @vocab = sort {$vocab->{$a} <=> $vocab->{$b}} keys %$vocab;
    for (my $i = 0; $i < @vocab; $i++) {
	print V "$vocab[$i]\t$i\n";
    }
    close(V);
}
